from __future__ import annotations
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Iterable, Self
import logging

from .base import VideoProfile, AudioProfile, Container, \
  AudioCodec, VideoCodec, Formats, VideoFormat, VideoProfiles, \
  AudioProfiles, Containers, VideoFormats, Subtitles, Subtitle
from .parse import Yaml, get_yaml, DEVICE_INFO, Fmts
from .video import Video, get_video_profiles
from .exceptions import UnknownFormat


@dataclass(eq=True, frozen=True)
class Device:
  name: str

  video_profiles: VideoProfiles = field(default_factory=VideoProfiles)
  audio_profiles: AudioProfiles = field(default_factory=AudioProfiles)

  containers: Containers = field(default_factory=Containers)
  subtitles: Subtitles = field(default_factory=Subtitles)

  @classmethod
  def from_yaml(cls, path: Path = DEVICE_INFO) -> Iterable[Self]:
    yaml = get_yaml(path)
    yield from get_devices(yaml)

  def add_format(self, fmt: VideoFormat):
    match fmt:
      case VideoProfile() as profile:
        self.video_profiles.append(profile)

      case AudioProfile() as profile:
        self.audio_profiles.append(profile)

      case Container() as container:
        self.containers.append(container)

      case Subtitle() as subtitle:
        self.subtitles.append(subtitle)

      case _:
        raise TypeError(f"Not a format: {fmt}")

  def add_formats(self, fmts: VideoFormats):
    for fmt in fmts:
      self.add_format(fmt)

  def can_play_audio(self, video: Video) -> bool:
    *_, audio_profile, _ = video.formats

    if audio_profile.codec is AudioCodec.unknown:
      raise UnknownFormat(f"Missing codec for {video}")

    can_play = any(video.is_compatible(profile) for profile in self.audio_profiles)

    if not can_play:
      logging.info(f"{audio_profile} not compatible with {self.audio_profiles}")

    return can_play

  def can_play_video(self, video: Video) -> bool:
    _, video_profile, *_ = video.formats

    if video_profile.codec is VideoCodec.unknown:
      raise UnknownFormat(f"Missing codec for {video}")

    can_play = any(video.is_compatible(profile) for profile in self.video_profiles)

    if not can_play:
      logging.info(f"{video_profile} not compatible with {self.video_profiles}")

    return can_play

  def can_play_container(self, video: Video) -> bool:
    container = video.formats.container

    if container is Container.unknown:
      raise UnknownFormat(f"Missing container for {video}")

    if not (can_play := container in self.containers):
      logging.info(f"{container} not compatible with {self.containers}")

    return can_play

  def can_play_subtitle(self, video: Video) -> bool:
    can_play = any(video.is_compatible(sub) for sub in self.subtitles)
    return can_play

  def can_play(self, video: Video) -> bool:
    return (
      self.can_play_audio(video) and
      self.can_play_video(video) and
      self.can_play_container(video) and
      self.can_play_subtitle(video)
    )

  def transcode_to(self, video: Video) -> Formats | None:
    return transcode_to(self, video)


def get_device(
  name: str,
  profiles: Yaml,
  container_names: Fmts,
  audio_names: Fmts,
  subtitle_names: Fmts,
) -> Device:
  device = Device(name)

  video = get_video_profiles(profiles)
  containers = map(Container.from_info, container_names)
  codecs = map(AudioCodec.from_info, audio_names)
  audio = map(AudioProfile, codecs)
  subtitles = map(Subtitle.from_info, subtitle_names)

  formats = chain(audio, video, containers, subtitles)
  device.add_formats(formats)

  return device


def get_devices(data: Yaml) -> Iterable[Device]:
  containers: Fmts = data['containers']
  audio: Fmts = data['audio']
  subtitles: Fmts = data['subtitles']

  for name, device_info in data['devices'].items():
    profiles: Yaml = device_info['profiles']
    yield get_device(name, profiles, containers, audio, subtitles)


def transcode_video(
  device: Device,
  video: Video,
  default_video: VideoProfile | None = None,
) -> VideoProfile | None:
  if device.can_play_video(video):
    return None

  _, video_profile, *_ = video.formats

  if not default_video:
    default_video, *_ = device.video_profiles

  return transcode_video_profile(video_profile, default_video)


def transcode_audio(
  device: Device,
  video: Video,
  default_audio: AudioProfile | None = None,
) -> AudioProfile | None:
  if device.can_play_audio(video):
    return None

  *_, audio_profile, _ = video.formats

  if not default_audio:
    default_audio, *_ = device.audio_profiles

  return transcode_audio_profile(audio_profile, default_audio)


def transcode_container(
  device: Device,
  video: Video,
  default_container: Container | None = None,
) -> Container | None:
  if device.can_play_container(video):
    return None

  container, *_ = video.formats

  if not default_container:
    default_container, *_ = device.containers

  return transcode_containers(container, default_container)


def transcode_subtitle(
  device: Device,
  video: Video,
  default_subtitle: Subtitle | None = None,
) -> Subtitle | None:
  # TODO: Finish this stub
  *_, subtitle = video.formats

  if not default_subtitle:
    default_subtitle, *_ = device.subtitles

  return transcode_subtitles(subtitle, default_subtitle)


def transcode_to(
  device: Device,
  video: Video,
  default_video: VideoProfile | None = None,
  default_audio: AudioProfile | None = None,
  default_container: Container | None = None,
  default_subtitle: Subtitle | None = None,
) -> Formats | None:
  if device.can_play(video):
    return None

  new_video = transcode_video(device, video, default_video)
  new_audio = transcode_audio(device, video, default_audio)
  new_container = transcode_container(device, video, default_container)
  new_subtitle = transcode_subtitle(device, video, default_subtitle)

  return Formats(
    container=new_container,
    video_profile=new_video,
    audio_profile=new_audio,
    subtitle=new_subtitle,
  )


def transcode_video_profile(
  video_profile: Formats,
  default_video: VideoProfile,
) -> VideoProfile:
  codec, resolution, fps, level = video_profile

  new_codec = None if codec is default_video.codec else default_video.codec
  new_resolution = None if resolution <= default_video.resolution else default_video.resolution
  new_fps = None if fps <= default_video.fps else default_video.fps
  new_level = None if level <= default_video.level else default_video.level
  new_level = new_level if new_codec is None else None

  return VideoProfile(
    codec=new_codec,
    resolution=new_resolution,
    fps=new_fps,
    level=new_level,
  )


def transcode_audio_profile(
  audio_profile: AudioProfile,
  default_audio: AudioProfile,
) -> AudioProfile:
  [codec] = audio_profile
  new_codec = None if codec is default_audio.codec else default_audio.codec

  return AudioProfile(new_codec)


def transcode_containers(
  container: Container,
  default_container: Container,
) -> Container | None:
  new_container = None if container is default_container else default_container

  return new_container


def transcode_subtitles(
  subtitle: Subtitle,
  default_subtitle: Subtitle,
) -> Subtitle | None:
  # TODO: Finish this stub
  return None


def transcode_formats(formats: Formats, default_formats: Formats) -> Formats | None:
  if formats == default_formats:
    return None

  container, video_profile, audio_profile, subtitle = formats
  default_container, default_video, default_audio, default_subtitle = default_formats

  new_video = transcode_video_profile(video_profile, default_video)
  new_audio = transcode_audio_profile(audio_profile, default_audio)
  new_container = transcode_containers(container, default_container)
  new_subtitle = transcode_subtitle(subtitle, default_subtitle)

  return Formats(
    container=new_container,
    video_profile=new_video,
    audio_profile=new_audio,
    subtitle=new_subtitle,
  )
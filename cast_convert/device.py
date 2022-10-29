from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Self
import logging

from .old.exceptions import UnknownCodec
from .base import VideoProfile, AudioProfile, Container, \
  AudioCodec, VideoCodec, Formats, Format
from .parse import Yaml, get_yaml, DEVICE_INFO
from .video import Video, get_video_profiles


@dataclass(eq=True, frozen=True)
class Device:
  name: str

  video_profiles: list[VideoProfile] = field(default_factory=list)
  audio_profiles: list[AudioProfile] = field(default_factory=list)

  containers: list[Container] = field(default_factory=list)

  @classmethod
  def from_yaml(cls, path: Path = DEVICE_INFO) -> Iterable[Self]:
    yaml = get_yaml(path)
    yield from get_devices(yaml)

  def add_format(self, fmt: Format):
    match fmt:
      case VideoProfile() as profile:
        self.video_profiles.append(profile)

      case AudioProfile() as profile:
        self.audio_profiles.append(profile)

      case Container() as container:
        self.containers.append(container)

      case _:
        raise TypeError(f"Not encodable: {fmt}")

  def can_play_audio(self, video: Video) -> bool:
    *_, audio_profile = video.formats

    if audio_profile.codec == AudioCodec.unknown:
      raise UnknownCodec(f"Missing codec for {video}")

    can_audio = any(video.is_compatible(profile) for profile in self.audio_profiles)

    if not can_audio:
      logging.info(f"{audio_profile} not compatible with {self.audio_profiles}")

    return can_audio

  def can_play_video(self, video: Video) -> bool:
    _, video_profile, _ = video.formats

    if video_profile.codec == VideoCodec.unknown:
      raise UnknownCodec(f"Missing codec for {video}")

    can_video = any(video.is_compatible(profile) for profile in self.video_profiles)

    if not can_video:
      logging.info(f"{video_profile} not compatible with {self.video_profiles}")

    return can_video

  def can_play_container(self, video: Video) -> bool:
    container = video.formats.container

    if not (can_container := container in self.containers):
      logging.info(f"{container} not compatible with {self.containers}")

    return can_container

  def can_play(self, video: Video) -> bool:
    return self.can_play_audio(video) and self.can_play_video(video) and self.can_play_container(video)

  def transcode_to(self, video: Video) -> Formats | None:
    return transcode_to(self, video)


def get_device(name: str, device_info: Yaml, data: Yaml) -> Device:
  names = map(AudioCodec.from_info, data['audio'])

  audio = list(map(AudioProfile, names))
  video = list(get_video_profiles(device_info['codecs']))
  containers = list(map(Container.from_info, data['containers']))

  return Device(name, video, audio, containers)


def get_devices(data: Yaml) -> Iterable[Device]:
  for name, device_info in data['devices'].items():
    yield get_device(name, device_info, data)


def transcode_video(
  device: Device,
  video: Video,
  default_video: VideoProfile | None = None,
) -> VideoProfile | None:
  if device.can_play_video(video):
    return None

  _, video_profile, _ = video.formats
  codec, resolution, fps, level = video_profile

  if not default_video:
    default_video, *_ = device.video_profiles

  new_codec = None if codec == default_video.codec else default_video.codec
  new_resolution = None if resolution <= default_video.resolution else default_video.resolution
  new_fps = None if fps <= default_video.fps else default_video.fps
  new_level = None if level <= default_video.level else default_video.level

  return VideoProfile(
    codec=new_codec,
    resolution=new_resolution,
    fps=new_fps,
    level=new_level,
  )

def transcode_audio(
  device: Device,
  video: Video,
  default_audio: AudioProfile | None = None,
) -> AudioProfile | None:
  if device.can_play_audio(video):
    return None

  *_,  audio_profile = video.formats
  [codec] = audio_profile

  if not default_audio:
    default_audio, *_ = device.audio_profiles

  new_codec = None if codec == default_audio.codec else default_audio.codec
  return AudioProfile(
    codec=new_codec
  )

def transcode_container(
  device: Device,
  video: Video,
  default_container: Container | None = None,
) -> Container | None:
  container, *_ = video.formats

  if device.can_play_container(video):
    return None

  if not default_container:
    default_container, *_ = device.containers

  new_container = None if container == default_container else default_container

  return new_container


def transcode_to(
  device: Device,
  video: Video,
  default_video: VideoProfile | None = None,
  default_audio: AudioProfile | None = None,
  default_container: Container | None = None,
) -> Formats | None:
  if device.can_play(video):
    return None

  new_video = transcode_video(device, video, default_video)
  new_audio = transcode_audio(device, video, default_audio)
  new_container = transcode_container(device, video, default_container)

  return Formats(
    container=new_container,
    video_profile=new_video,
    audio_profile=new_audio,
  )



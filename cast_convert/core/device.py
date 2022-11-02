from __future__ import annotations
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Iterable, Self, Type
import logging

from .models.profiles import AudioProfile, VideoProfile
from .models.formats import (
  AudioProfiles, Containers,
  Formats, Subtitles, VideoFormat, VideoFormats, VideoProfiles,
)
from .models.codecs import AudioCodec, Container, Subtitle, VideoCodec
from .parse import Yaml, get_yaml, DEVICE_INFO, Fmts
from .transcode import transcode_to
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
  def from_yaml(cls: Type[Self], path: Path = DEVICE_INFO) -> Iterable[Self]:
    yaml = get_yaml(path)
    yield from get_devices(yaml)

  @classmethod
  def from_attrs(
    cls: Type[Self],
    name: str,
    profiles: Yaml,
    container_names: Fmts,
    audio_names: Fmts,
    subtitle_names: Fmts,
  ) -> Self:
    return get_device(
      name,
      profiles,
      container_names,
      audio_names,
      subtitle_names,
    )

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
  video = get_video_profiles(profiles)
  containers = map(Container.from_info, container_names)
  codecs = map(AudioCodec.from_info, audio_names)
  audio = map(AudioProfile, codecs)
  subtitles = map(Subtitle.from_info, subtitle_names)

  device = Device(name)
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

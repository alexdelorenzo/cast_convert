from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from itertools import chain
from pathlib import Path
from typing import Iterable, Self, Type
import logging

from thefuzz import process

from .video import Video, get_video_profiles
from ..base import IsCompatible, MIN_FUZZY_MATCH_SCORE, first
from ..convert.transcode import transcode_to
from ..exceptions import UnknownFormat
from ..media.base import get_name
from ..media.codecs import AudioCodec, Container, Containers, Subtitle, Subtitles, VideoCodec
from ..media.formats import Formats, Metadata, VideoFormat, VideoFormats, are_compatible
from ..media.profiles import AudioProfile, AudioProfiles, VideoProfile, VideoProfiles
from ..parse import DEVICE_INFO, Fmts, Yaml, get_yaml


@dataclass(eq=True, frozen=True)
class Device(IsCompatible):
  name: str

  video_profiles: VideoProfiles = field(default_factory=VideoProfiles)
  audio_profiles: AudioProfiles = field(default_factory=AudioProfiles)

  containers: Containers = field(default_factory=Containers)
  subtitles: Subtitles = field(default_factory=Subtitles)

  @classmethod
  def from_yaml(
    cls: Type[Self],
    path: Path = DEVICE_INFO
  ) -> Iterable[Self]:
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

    if not audio_profile:
      return True

    if audio_profile.codec is AudioCodec.unknown:
      raise UnknownFormat(f"Missing codec for {video}")

    can_play = any(video.is_compatible(profile) for profile in self.audio_profiles)

    if not can_play:
      logging.info(f"{audio_profile} not compatible with {self.audio_profiles}")

    return can_play

  def can_play_video(self, video: Video) -> bool:
    _, video_profile, *_ = video.formats

    if not video_profile:
      return True

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

  def transcode_to(
    self,
    video: Video,
    default_video: VideoProfile | None = None,
    default_audio: AudioProfile | None = None,
    default_container: Container | None = None,
    default_subtitle: Subtitle | None = None,
  ) -> Formats | None:
    return transcode_to(
      self,
      video,
      default_video,
      default_audio,
      default_container,
      default_subtitle
    )

  def is_compatible(self, other: Metadata) -> bool:
    return is_compatible(self, other)


def get_device(
  name: str,
  profiles: Yaml,
  container_names: Fmts,
  audio_names: Fmts,
  subtitle_names: Fmts,
) -> Device:
  containers = map(Container.from_info, container_names)
  codecs = map(AudioCodec.from_info, audio_names)
  audio = map(AudioProfile, codecs)
  subtitles = map(Subtitle.from_info, subtitle_names)

  video = get_video_profiles(profiles)
  formats = chain(containers, audio, subtitles, video)

  device = Device(name)
  device.add_formats(formats)

  return device


def get_devices(data: Yaml) -> Iterable[Device]:
  containers: Fmts = data['containers']
  audio: Fmts = data['audio']
  subtitles: Fmts = data['subtitles']

  for name, device_info in data['devices'].items():
    profiles: Yaml = device_info['profiles']
    yield get_device(name, profiles, containers, audio, subtitles)


def is_compatible(device: Device, other: Metadata) -> bool:
  match other:
    case VideoProfile():
      return any(are_compatible(profile, other) for profile in device.video_profiles)

    case AudioProfile(codec):
      return any(are_compatible(profile.codec, codec) for profile in device.audio_profiles)

    case VideoCodec() as codec:
      return any(are_compatible(profile.codec, codec) for profile in device.video_profiles)

    case AudioCodec() as codec:
      return any(are_compatible(profile.codec, codec) for profile in device.audio_profiles)

    case Container() as _container:
      return any(are_compatible(container, _container) for container in device.containers)

    case Subtitle() as _sub:
      if not _sub:
        return True

      return any(are_compatible(sub, _sub) for sub in device.subtitles)

    case Formats() as formats:
      return all(device.is_compatible(fmt) for fmt in formats)

    case _:
      raise TypeError(f'Cannot compare device with {get_name(other)}')


Devices = tuple[Device, ...]


@lru_cache
def load_device_with_name(
  name: str,
  device_file: Path = DEVICE_INFO,
) -> Device | None:
  name = name.casefold()
  devices = get_devices_from_file(device_file)

  return get_device_fuzzy(name, devices)


def get_device_with_name(
  name: str,
  devices: Devices,
) -> Device | None:
  name = name.casefold()

  if not (dev := first(d for d in devices if d.name.casefold() == name)):
    return None

  return dev


@lru_cache
def get_devices_from_file(
  device_file: Path = DEVICE_INFO,
) -> Devices:
  devices: Devices = tuple(Device.from_yaml(device_file))
  return devices


def get_device_fuzzy(
  name: str,
  devices: Devices,
) -> Device | None:
  devices = {dev.name: dev for dev in devices}
  closest_name, score = process.extractOne(name, devices.keys())

  if score < MIN_FUZZY_MATCH_SCORE:
    return None

  return devices.get(closest_name)

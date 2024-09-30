from __future__ import annotations

from abc import ABC
from dataclasses import asdict, dataclass
from functools import cache
from typing import Final, TYPE_CHECKING

from unpackable import Unpackable

from .codecs import AudioCodec, Codec, Codecs, ProfileName, VideoCodec
from ..base import (
  CODEC_BIAS, NEW_LINE,
)
from ..protocols import AsDict, AsText, HasItems, HasName, HasWeight, IsCompatible, NO_BIAS, get_name
from ..types import DEFAULT_PROFILE_FPS, DEFAULT_PROFILE_LEVEL, DEFAULT_PROFILE_RESOLUTION, Fps, Level, \
  Resolution, WithName


if TYPE_CHECKING:
  from .formats import Metadata


ACRONYM_LIMIT: Final[int] = 3


@dataclass(eq=True, frozen=True)
class Profile(
  ABC,
  AsDict,
  AsText,
  HasItems,
  HasWeight,
  IsCompatible,
  WithName,
  Unpackable
):
  codec: Codecs

  @property
  def as_dict(self) -> dict[str, Metadata]:
    return asdict(self)

  @property
  def text(self) -> str:
    return NEW_LINE.join(
      format_label(key, val)
      for key, val in self.as_dict.items()
      if val is not None
    )

  @property
  def count(self) -> int:
    """Return a count of non-null formats belonging to Profile"""
    return sum(fmt is not None for fmt in self)

  @property
  def bias(self) -> int:
    return CODEC_BIAS if self.codec else NO_BIAS

  @property
  def weight(self) -> int:
    return self.count + self.bias


@dataclass(eq=True, frozen=True)
class AudioProfile(Profile, IsCompatible):
  """Audio Profile"""
  codec: AudioCodec | None = AudioCodec.unknown

  def __repr__(self) -> str:
    return f"{get_name(self)}({self.codec})"

  def is_compatible(self, other: Metadata) -> bool:
    match other:
      case AudioProfile() as profile:
        return is_codec_compatible(self.codec, profile.codec)

      case AudioCodec() as codec:
        return is_codec_compatible(self.codec, codec)

    super().is_compatible(other)


@dataclass(eq=True, frozen=True)
class VideoProfile(Profile, IsCompatible):
  """Video Profile"""
  codec: VideoCodec | None = VideoCodec.unknown
  resolution: Resolution | None = DEFAULT_PROFILE_RESOLUTION
  fps: Fps | None = DEFAULT_PROFILE_FPS
  level: Level | None = DEFAULT_PROFILE_LEVEL

  def is_compatible(self, other: Metadata) -> bool:
    match other:
      case VideoProfile() as profile:
        return is_video_profile_compatible(self, profile)

      case Resolution() as resolution:
        return is_resolution_compatible(self.resolution, resolution)

      case Fps() as fps:
        return is_fps_compatible(self.fps, fps)

      case Level() as level:
        return is_level_compatible(self.level, level)

    super().is_compatible(other)


@dataclass(eq=True, frozen=True)
class EncoderProfile(Profile):
  """Encoder Profile"""
  profile: ProfileName | None = None
  level: Level | None = None


type Profiles = AudioProfile | VideoProfile

VideoProfiles = list[VideoProfile]
AudioProfiles = list[AudioProfile]


def is_video_profile_compatible(
  profile: VideoProfile | None,
  supported: VideoProfile | None,
) -> bool:
  codec, resolution, fps, level = profile
  supported_codec, max_resolution, max_fps, max_level = supported

  return (
    is_codec_compatible(codec, supported_codec) and
    is_resolution_compatible(resolution, max_resolution) and
    is_fps_compatible(fps, max_fps) and
    is_level_compatible(level, max_level)
  )


def is_level_compatible(
  level: Level | None,
  max_level: Level | None,
) -> bool:
  return level is max_level or level <= max_level


def is_fps_compatible(
  fps: Fps | None,
  max_fps: Fps | None
) -> bool:
  return fps is max_fps or fps <= max_fps


def is_resolution_compatible(
  resolution: Resolution | None,
  max_resolution: Resolution | None
) -> bool:
  return resolution is max_resolution or resolution <= max_resolution


def is_codec_compatible(
  codec: Codecs | None,
  other: Codecs | None,
) -> bool:
  return codec is other or codec == other


@cache
def get_label(key: str, val: Metadata) -> str:
  match val:
    case Codec() | HasName() as has_name:
      label = has_name.name.title()

    case _:
      label = key.title()

  if len(label) <= ACRONYM_LIMIT:
    label = label.upper()

  return label


def format_label(key: str, val: Metadata) -> str:
  label = get_label(key, val)

  return f'[b]{label}[/]: [b blue]{val}[/]'

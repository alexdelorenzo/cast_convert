from __future__ import annotations

from abc import ABC
from dataclasses import asdict, dataclass
from typing import Final, TYPE_CHECKING

from unpackable import Unpackable

from .base import get_name
from .codecs import AudioCodec, Codecs, ProfileName, VideoCodec
from ..base import (
  AsDict, AsText, DEFAULT_PROFILE_FPS, DEFAULT_PROFILE_LEVEL,
  DEFAULT_PROFILE_RESOLUTION, Fps, Level, Resolution,
)

if TYPE_CHECKING:
  from .formats import Metadata


NO_BIAS: Final[int] = 0
CODEC_BIAS: Final[int] = 5
INCREMENT: Final[int] = 1


@dataclass(eq=True, frozen=True)
class Profile(ABC, AsDict, AsText, Unpackable):
  codec: Codecs

  @property
  def as_dict(self) -> dict[str, Metadata]:
    return asdict(self)

  @property
  def text(self):
    return '\n'.join(
      f'[b]{key.title()}[/]: [b blue]{val}[/]'
      for key, val in self.as_dict.items()
      if val is not None
    )

  @property
  def count(self) -> int:
    """Return a count of non-null formats belonging to Profile"""
    return sum(INCREMENT for fmt in self if fmt is not None)

  @property
  def bias(self) -> int:
    return CODEC_BIAS if self.codec else NO_BIAS

  @property
  def weight(self) -> int:
    return self.count + self.bias


@dataclass(eq=True, frozen=True)
class AudioProfile(Profile):
  codec: AudioCodec | None = AudioCodec.unknown

  def __repr__(self) -> str:
    return f"{get_name(self)}({self.codec})"


@dataclass(eq=True, frozen=True)
class VideoProfile(Profile):
  codec: VideoCodec | None = VideoCodec.unknown
  resolution: Resolution | None = DEFAULT_PROFILE_RESOLUTION
  fps: Fps | None = DEFAULT_PROFILE_FPS
  level: Level | None = DEFAULT_PROFILE_LEVEL


@dataclass(eq=True, frozen=True)
class EncoderProfile(Profile):
  profile: ProfileName | None = None
  level: Level | None = None


Profiles = AudioProfile | VideoProfile
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
  return codec is other


from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from unpackable import Unpackable

from ..base import (
  DEFAULT_PROFILE_FPS, DEFAULT_PROFILE_LEVEL,
  DEFAULT_PROFILE_RESOLUTION, Fps, Level, Resolution,
)
from .base import get_name
from .codecs import AudioCodec, ProfileName, VideoCodec


@dataclass(eq=True, frozen=True)
class Profile(ABC):
  pass


@dataclass(eq=True, frozen=True)
class AudioProfile(Profile, Unpackable):
  codec: AudioCodec | None = AudioCodec.unknown

  def __repr__(self) -> str:
    return f"{get_name(self)}({self.codec})"


@dataclass(eq=True, frozen=True)
class VideoProfile(Profile, Unpackable):
  codec: VideoCodec | None = VideoCodec.unknown
  resolution: Resolution | None = DEFAULT_PROFILE_RESOLUTION
  fps: Fps | None = DEFAULT_PROFILE_FPS
  level: Level | None = DEFAULT_PROFILE_LEVEL


@dataclass(eq=True, frozen=True)
class EncoderProfile(Profile, Unpackable):
  profile: ProfileName | None = None
  level: Level | None = None


Profiles = AudioProfile | VideoProfile
VideoProfiles = list[VideoProfile]
AudioProfiles = list[AudioProfile]


def is_video_profile_compatible(video_profile: VideoProfile, other: VideoProfile) -> bool:
  codec, resolution, fps, level = video_profile
  _codec, _resolution, _fps, _level = other

  return (
    codec is _codec and
    resolution <= _resolution and
    fps <= _fps and
    level <= _level
  )

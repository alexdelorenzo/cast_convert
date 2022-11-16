from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from unpackable import Unpackable

from ..base import (
  DEFAULT_PROFILE_FPS, DEFAULT_PROFILE_LEVEL,
  DEFAULT_PROFILE_RESOLUTION, Fps, Level, Resolution,
)
from .base import get_name
from .codecs import AudioCodec, Codecs, ProfileName, VideoCodec


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


def is_video_profile_compatible(
  profile: VideoProfile,
  supported: VideoProfile
) -> bool:
  codec, resolution, fps, level = profile
  supported_codec, max_resolution, max_fps, max_level = supported

  return (
    is_codec_compatible(codec, supported_codec) and
    is_resolution_compatible(resolution, max_resolution) and
    is_fps_compatible(fps, max_fps) and
    is_level_compatible(level, max_level)
  )


def is_level_compatible(level: Level, max_level: Level) -> bool:
  return level is max_level or level <= max_level


def is_fps_compatible(fps: Fps, max_fps: Fps) -> bool:
  return fps is max_fps or fps <= max_fps


def is_resolution_compatible(
  resolution: Resolution,
  max_resolution: Resolution
) -> bool:
  return resolution is max_resolution or resolution <= max_resolution


def is_codec_compatible(
  codec: Codecs | None,
  other: Codecs | None,
) -> bool:
  return codec is other

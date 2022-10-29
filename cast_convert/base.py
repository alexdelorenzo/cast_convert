from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Final, Self, Type
from abc import ABC
from pathlib import Path
import logging

from unpackable import Unpackable


logging.basicConfig(level=logging.WARN)


INFO: Final[Path] = Path('chromecasts.yml')


class CastConvertException(Exception):
  pass


class VideoError(CastConvertException):
  pass


class UnknownCodec(VideoError):
  pass


class Normalize:
  unknown: str

  @classmethod
  def _missing_(cls, value: str) -> Self:
    print(f"[{cls.__name__}] Not enumerated: {value}")
    return cls.unknown

  @classmethod
  def from_info(cls: Type[Self], info: str) -> Self:
    normalized = normalize_info(info)
    return cls(normalized)


class Container(Normalize, StrEnum):
  mp2t: str = auto()
  mp3: str = auto()
  mp4: str = auto()
  mpeg4: str = auto()
  ogg: str = auto()
  wav: str = auto()
  webm: str = auto()
  matroska: str = auto()

  unknown: str = auto()


class VideoCodec(Normalize, StrEnum):
  avc: str = auto()
  mpeg4: str = auto()
  h264: str = auto()
  h265: str = auto()
  hevc: str = auto()
  vp8: str = auto()
  vp9: str = auto()
  hdr: str = auto()

  unknown: str = auto()


class AudioCodec(Normalize, StrEnum):
  aac: str = auto()
  eacs: str = auto()
  flac: str = auto()
  heaac: str = auto()
  lcaac: str = auto()
  opus: str = auto()
  vorbis: str = auto()
  wav: str = auto()
  webm: str = auto()
  mp3: str = auto()

  unknown: str = auto()


@dataclass(eq=True, frozen=True)
class Profile(ABC):
  pass


@dataclass(eq=True, frozen=True)
class AudioProfile(Profile, Unpackable):
  codec: AudioCodec = AudioCodec.unknown


@dataclass(eq=True, frozen=True)
class VideoProfile(Profile, Unpackable):
  codec: VideoCodec = VideoCodec.unknown
  resolution: int = 720
  fps: float = 24.0
  level: float | None = 0.0


def normalize_info(info: str) -> str:
  info = info.casefold()
  return ''.join(char for char in info if char.isalnum())

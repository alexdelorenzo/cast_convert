from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Final, Self, Type, Iterable, TypeVar, NamedTuple
from decimal import Decimal
from abc import ABC
import logging

from unpackable import Unpackable

from .exceptions import UnknownFormat
from .parse import ALIAS_FMTS, EXTENSIONS, Extension


logging.basicConfig(level=logging.WARN)


PROFILE_SEP: Final[str] = '@L'


T = TypeVar('T')
U = TypeVar('U')

Item = T | U | None

Level = Decimal
Fps = Decimal


DEFAULT_FPS: Final[Fps] = Fps()
DEFAULT_LEVEL: Final[Level] = Level()


class NormalizedFormat:
  unknown: str

  @classmethod
  def _missing_(cls: Type[Self], value: str) -> Self:
    logging.info(f"[{cls.__name__}] Not enumerated: {value}")

    if name := ALIAS_FMTS.get(value):
      return cls(name)

    return cls.unknown

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self:
    if not info:
      return cls.unknown

    if not isinstance(info, str):
      raise TypeError(f"{cls.__name__}: Can't normalize: {info}")

    normalized = normalize_info(info)
    return cls(normalized)


class Container(NormalizedFormat, StrEnum):
  unknown: str = auto()
  avi: str = auto()
  matroska: str = auto()
  mp2t: str = auto()
  mp3: str = auto()
  mp4: str = auto()
  mpeg4: str = auto()
  ogg: str = auto()
  wav: str = auto()
  webm: str = auto()

  def to_extension(self) -> Extension | None:
    if ext := EXTENSIONS.get(self):
      return ext

    logging.info(f"Can't find {self.name} in {EXTENSIONS}")
    return None


class VideoCodec(NormalizedFormat, StrEnum):
  unknown: str = auto()
  avc: str = auto()
  divx: str = auto()
  h264: str = auto()
  h265: str = auto()
  hdr: str = auto()
  hevc: str = auto()
  mpeg4: str = auto()
  vp8: str = auto()
  vp9: str = auto()
  xvid: str = auto()


class AudioCodec(NormalizedFormat, StrEnum):
  unknown: str = auto()
  aac: str = auto()
  ac3: str = auto()
  eac3: str = auto()
  eacs: str = auto()
  flac: str = auto()
  heaac: str = auto()
  lcaac: str = auto()
  mp3: str = auto()
  opus: str = auto()
  vorbis: str = auto()
  wav: str = auto()
  webm: str = auto()


class Subtitle(NormalizedFormat, StrEnum):
  unknown: str = auto()
  ass: str = auto()
  utf8: str = auto()

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self | None:
    if not info:
      return None

    elif '/' in info:
      info, *_ = info.split('/')

    info = info.strip()

    return super().from_info(info)


@dataclass(eq=True, frozen=True)
class Profile(ABC):
  pass


@dataclass(eq=True, frozen=True)
class AudioProfile(Profile, Unpackable):
  codec: AudioCodec | None = AudioCodec.unknown


@dataclass(eq=True, frozen=True)
class VideoProfile(Profile, Unpackable):
  codec: VideoCodec | None = VideoCodec.unknown
  resolution: int | None = 720
  fps: Fps | None = Fps('24.0')
  level: Level | None = Level('0.0')


VideoProfiles = list[VideoProfile]
AudioProfiles = list[AudioProfile]
Containers = list[Container]
Subtitles = list[Subtitle]

MediaFormat = VideoProfile | AudioProfile | Container | Subtitle
MediaFormats = Iterable[MediaFormat]


class Formats(NamedTuple):
  container: Container | None = None
  video_profile: VideoProfile | None = None
  audio_profile: AudioProfile | None = None
  subtitle: Subtitle | None = None


def normalize_info(info: str) -> str:
  info = info.casefold()
  return ''.join(char for char in info if char.isalnum())


def first(iterable: Iterable[T], default: Item = None) -> Item:
  iterator = iter(iterable)
  return next(iterator, default)

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Final, Self, Type, Iterable, TypeVar, NamedTuple, Any
from decimal import Decimal
from abc import ABC
import logging

from unpackable import Unpackable

from .exceptions import UnknownFormat
from .parse import ALIAS_FMTS, EXTENSIONS, Extension


logging.basicConfig(level=logging.INFO)


PROFILE_SEP: Final[str] = '@L'
SUBTITLE_SEP: Final[str] = '/'


T = TypeVar('T')
U = TypeVar('U')

Item = T | U | None

Level = Decimal
Fps = Decimal


DEFAULT_VIDEO_FPS: Final[Fps] = Fps()
DEFAULT_VIDEO_LEVEL: Final[Level] = Level()

DEFAULT_PROFILE_FPS: Final[Fps] = Fps('24.0')
DEFAULT_PROFILE_LEVEL: Final[Level] = Level('0.0')
DEFAULT_PROFILE_RESOLUTION: Final[int] = 720


class NormalizedFormat:
  unknown: str

  @classmethod
  def _missing_(cls: Type[Self], value: str) -> Self:
    logging.info(f"[{get_name(cls)}] Not enumerated: {value}")

    if name := ALIAS_FMTS.get(value):
      return cls(name)

    return cls.unknown

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self:
    if not info:
      return cls.unknown

    if not isinstance(info, str):
      raise TypeError(f"[{get_name(cls)}] Can't normalize: {info}")

    normalized = normalize_info(info)
    return cls(normalized)

  def __repr__(self) -> str:
    return f"{get_name(self)}({self})"


class Container(NormalizedFormat, StrEnum):
  unknown: str = auto()
  avi: str = auto()
  matroska: str = auto()
  mp2t: str = auto()
  mp3: str = auto()
  mp4: str = auto()
  # mpeg4: str = auto()
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
  srt: str = auto()
  ssa: str = auto()
  vtt: str = auto()
  ttml: str = auto()
  eia608: str = auto()
  eia708: str = auto()

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self | None:
    if not info:
      return None

    elif SUBTITLE_SEP in info:
      info, *_ = info.split(SUBTITLE_SEP)

    info = info.strip()
    return super().from_info(info)


@dataclass(eq=True, frozen=True)
class Profile(ABC):
  pass


@dataclass(eq=True, frozen=True)
class AudioProfile(Profile, Unpackable):
  codec: AudioCodec | None = AudioCodec.unknown

  def __repr__(self) -> str:
    name = get_name(self)
    return f"{name}({self.codec})"


@dataclass(eq=True, frozen=True)
class VideoProfile(Profile, Unpackable):
  codec: VideoCodec | None = VideoCodec.unknown
  resolution: int | None = DEFAULT_PROFILE_RESOLUTION
  fps: Fps | None = DEFAULT_PROFILE_FPS
  level: Level | None = DEFAULT_PROFILE_LEVEL


VideoProfiles = list[VideoProfile]
AudioProfiles = list[AudioProfile]
Containers = list[Container]
Subtitles = list[Subtitle]

Codecs = AudioCodec | VideoCodec
Profiles = AudioProfile | VideoProfile
VideoMetadata = Codecs | Profiles | Container

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


def get_name(obj: Any) -> str:
  match obj:
    case type() as cls:
      return cls.__name__

    case _:
      return type(obj).__name__

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Final, Self, Type, Iterable, TypeVar, \
  NamedTuple, Any, Callable
from decimal import Decimal
from abc import ABC
import logging

from unpackable import Unpackable

from .exceptions import UnknownFormat
from .parse import ALIAS_FMTS, EXTENSIONS, Extension


logging.basicConfig(level=logging.INFO)


AT: Final[str] = '@'
LEVEL_SEP: Final[str] = 'L'
PROFILE_SEP: Final[str] = AT + LEVEL_SEP
SUBTITLE_SEP: Final[str] = '/'


T = TypeVar('T')
U = TypeVar('U')

Item = T | U | None


class Decimal(Decimal):  # type: ignore
  def __repr__(self) -> str:
    return str(self)


Fps = Decimal
Level = Decimal


DEFAULT_VIDEO_FPS: Final[Fps] = Fps()
DEFAULT_VIDEO_LEVEL: Final[Level] = Level()

DEFAULT_PROFILE_FPS: Final[Fps] = Fps('24.0')
DEFAULT_PROFILE_LEVEL: Final[Level] = Level('0.0')
DEFAULT_PROFILE_RESOLUTION: Final[int] = 720


class NormalizedFormat:
  unknown: str

  def __repr__(self) -> str:
    return f"{get_name(self)}({self})"

  @classmethod
  def _missing_(cls: Type[Self], value: str) -> Self:
    name = get_name(cls)
    logging.info(f"[{name}] Missing: {value}")

    if hasattr(cls, value):
      return getattr(cls, value)

    if alias := ALIAS_FMTS.get(value):
      logging.info(f"[{name}] Using {alias} as an alias for {value}")
      return cls(alias)

    logging.info(f"[{name}] Not found, using `unknown` instead of {value}")
    return cls.unknown

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self:
    if not info:
      return cls.unknown

    if not isinstance(info, str):
      raise TypeError(f"[{get_name(cls)}] Can't normalize: {info}")

    normalized = normalize_info(info)
    return cls(normalized)


class Container(NormalizedFormat, StrEnum):
  unknown: str = auto()
  avi: str = auto()
  matroska: str = auto()
  mkv: str = matroska  # alias
  mp2t: str = auto()
  mp3: str = auto()
  mp4: str = auto()
  mpeg4: str = mp4  # alias
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
  h264: str = avc  # alias
  div3: str = auto()
  divx: str = div3  # alias
  mpeg4visual: str = divx
  hevc: str = auto()
  h265: str = hevc  # alias
  hdr: str = auto()
  mpeg4: str = auto()
  mp4: str = avc  # alias
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
  webvtt: str = auto()
  vtt: str = webvtt  # alias
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


class ProfileName(NormalizedFormat, StrEnum):
  main: str = auto()
  main10: str = auto()


@dataclass(eq=True, frozen=True)
class Profile(ABC):
  pass


def get_name(obj: Any) -> str:
  match obj:
    case type() as cls:
      return cls.__name__

    case _:
      return type(obj).__name__


@dataclass(eq=True, frozen=True)
class AudioProfile(Profile, Unpackable):
  codec: AudioCodec | None = AudioCodec.unknown

  def __repr__(self) -> str:
    return f"{get_name(self)}({self.codec})"


@dataclass(eq=True, frozen=True)
class VideoProfile(Profile, Unpackable):
  codec: VideoCodec | None = VideoCodec.unknown
  resolution: int | None = DEFAULT_PROFILE_RESOLUTION
  fps: Fps | None = DEFAULT_PROFILE_FPS
  level: Level | None = DEFAULT_PROFILE_LEVEL


@dataclass(eq=True, frozen=True)
class EncoderProfile(Profile, Unpackable):
  profile: ProfileName | None = None
  level: Level | None = None


VideoProfiles = list[VideoProfile]
AudioProfiles = list[AudioProfile]
Containers = list[Container]
Subtitles = list[Subtitle]

Codecs = AudioCodec | VideoCodec
Profiles = AudioProfile | VideoProfile
VideoFormat = Codecs | Profiles | Container | Subtitle
VideoFormats = Iterable[VideoFormat]


class Formats(NamedTuple):
  container: Container | None = None
  video_profile: VideoProfile | None = None
  audio_profile: AudioProfile | None = None
  subtitle: Subtitle | None = None


class OnTranscodeErr(NormalizedFormat, StrEnum):
  cycle_video_encoders: str = auto()
  cycle_audio_encoders: str = auto()


def normalize_info(
  info: str,
  condition: Callable[[str], bool] = str.isalnum
) -> str:
  info = info.casefold()

  return ''.join(
    char
    for char in info
    if condition(char)
  )


def first(iterable: Iterable[T], default: Item = None) -> Item:
  iterator = iter(iterable)
  return next(iterator, default)
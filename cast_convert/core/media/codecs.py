from __future__ import annotations

import logging
from enum import Enum, StrEnum, auto
from typing import Self, Type, TypeVar

from .base import NormalizedFormat
from ..base import SUBTITLE_SEP
from ..parse import EXTENSIONS, Extension


E = TypeVar('E', bound=Enum | str)


def alias(val: E) -> E:
  """Denotes an Enum's alias"""
  return val


class Container(NormalizedFormat, StrEnum):
  """File Container"""
  avi: Self = auto()
  matroska: Self = auto()
  mkv: Self = alias(matroska)
  mp2t: Self = auto()
  mp3: Self = auto()
  mp4: Self = auto()
  mpegts: Self = auto()
  isom: Self = alias(mp4)
  mpeg4: Self = alias(mp4)
  ogg: Self = auto()
  wav: Self = auto()
  webm: Self = auto()
  invalid: Self = auto()
  unknown: Self = auto()

  def to_extension(self) -> Extension | None:
    if ext := EXTENSIONS.get(self):
      return ext

    logging.warning(f"Can't find {self.name} in {EXTENSIONS}")
    return None


class Codec(NormalizedFormat, StrEnum):
  pass


class VideoCodec(Codec):
  """Video Codec"""
  avc: Self = auto()
  div3: Self = auto()
  divx: Self = alias(div3)
  h264: Self = alias(avc)
  hdr: Self = auto()
  hevc: Self = auto()
  h265: Self = alias(hevc)
  mp4: Self = alias(avc)
  mpeg4: Self = auto()
  mpeg4visual: Self = alias(divx)
  vp8: Self = auto()
  vp9: Self = auto()
  vp09: Self = alias(vp9)
  xvid: Self = auto()
  unknown: Self = auto()


class AudioCodec(Codec):
  """Audio Codec"""
  aac: Self = auto()
  ac3: Self = auto()
  eac3: Self = auto()
  eacs: Self = auto()
  dts: Self = auto()
  flac: Self = auto()
  heaac: Self = auto()
  lcaac: Self = auto()
  mp3: Self = auto()
  opus: Self = auto()
  vorbis: Self = auto()
  wav: Self = auto()
  webm: Self = auto()
  wma: Self = auto()
  unknown: Self = auto()


class Subtitle(NormalizedFormat, StrEnum):
  ass: Self = auto()
  eia608: Self = auto()
  eia708: Self = auto()
  srt: Self = auto()
  utf8: Self = alias(srt)
  ssa: Self = auto()
  ttml: Self = auto()
  unknown: Self = auto()
  webvtt: Self = auto()
  vtt: Self = alias(webvtt)
  dwebvtt: Self = alias(webvtt)

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self | None:
    if not info:
      return None

    elif SUBTITLE_SEP in info:
      info, *_ = info.split(SUBTITLE_SEP)

    info = info.strip()
    return super().from_info(info)


class ProfileName(NormalizedFormat, StrEnum):
  main: Self = auto()
  main10: Self = auto()


Containers = list[Container]
Subtitles = list[Subtitle]
Codecs = AudioCodec | VideoCodec

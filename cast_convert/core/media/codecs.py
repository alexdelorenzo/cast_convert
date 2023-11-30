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
  avi = auto()
  matroska = auto()
  mkv = alias(matroska)
  mp2t = auto()
  mp3 = auto()
  mp4 = auto()
  mpegts = auto()
  isom = alias(mp4)
  mpeg4 = alias(mp4)
  ogg = auto()
  wav = auto()
  webm = auto()
  invalid = auto()
  unknown = auto()

  def to_extension(self) -> Extension | None:
    if ext := EXTENSIONS.get(self):
      return ext

    logging.warning(f"Can't find {self.name} in {EXTENSIONS}")
    return None


class Codec(NormalizedFormat, StrEnum):
  pass


class VideoCodec(Codec):
  """Video Codec"""
  avc = auto()
  div3 = auto()
  divx = alias(div3)
  h264 = alias(avc)
  hdr = auto()
  hevc = auto()
  h265 = alias(hevc)
  mp4 = alias(avc)
  mpeg4 = auto()
  mpeg4visual = alias(divx)
  vp8 = auto()
  vp9 = auto()
  vp09 = alias(vp9)
  xvid = auto()
  unknown = auto()


class AudioCodec(Codec):
  """Audio Codec"""
  aac = auto()
  ac3 = auto()
  eac3 = auto()
  eacs = auto()
  dts = auto()
  flac = auto()
  heaac = auto()
  lcaac = auto()
  mp3 = auto()
  opus = auto()
  vorbis = auto()
  wav = auto()
  webm = auto()
  wma = auto()
  unknown = auto()


class Subtitle(NormalizedFormat, StrEnum):
  ass = auto()
  eia608 = auto()
  eia708 = auto()
  srt = auto()
  utf8 = alias(srt)
  ssa = auto()
  ttml = auto()
  unknown = auto()
  webvtt = auto()
  vtt = alias(webvtt)
  dwebvtt = alias(webvtt)

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self | None:
    if not info:
      return None

    elif SUBTITLE_SEP in info:
      info, *_ = info.split(SUBTITLE_SEP)

    info = info.strip()
    return super().from_info(info)


class ProfileName(NormalizedFormat, StrEnum):
  main = auto()
  main10 = auto()


Containers = list[Container]
Subtitles = list[Subtitle]
Codecs = AudioCodec | VideoCodec

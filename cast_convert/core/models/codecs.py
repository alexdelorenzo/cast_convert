from __future__ import annotations

import logging
from enum import StrEnum, auto
from typing import Self, Type

from ..base import SUBTITLE_SEP
from ..parse import EXTENSIONS, Extension
from .base import NormalizedFormat


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

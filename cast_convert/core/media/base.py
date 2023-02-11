from __future__ import annotations

import logging
from enum import StrEnum, auto
from typing import Self, Type

from ..base import WithName, get_name
from ..fmt import normalize
from ..parse import ALIAS_FMTS


class NormalizedFormat(WithName):
  unknown: Self | str

  def __bool__(self) -> bool:
    return self != self.unknown

  def __repr__(self) -> str:
    return f"{get_name(self)}({self})"

  @classmethod
  def _missing_(cls: Type[Self], value: str) -> Self:
    name = get_name(cls)
    logging.info(f"[{name}] Missing: {value}")

    if alias := getattr(cls, value, None):
      logging.info(f"[{name}] Using {alias} as an alias for {value}")
      return alias

    if alias := ALIAS_FMTS.get(value):
      logging.info(f"[{name}] Using {alias} as an alias for {value}")
      return cls(alias)

    logging.info(f"[{name}] Not found, using `unknown` instead of {value}")
    return cls.unknown

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self:
    name = get_name(cls)

    if not info:
      logging.info(f"[{name}] no info supplied: {info}")
      return cls.unknown

    if not isinstance(info, str):
      raise TypeError(f"[{name}] Can't normalize: {info}")

    normalized = normalize(info)
    logging.debug(f'{name}({info}) normalized as {name}({normalized})')

    return cls(normalized)


class OnTranscodeErr(NormalizedFormat, StrEnum):
  cycle_video_encoders: OnTranscodeErr = auto()
  cycle_audio_encoders: OnTranscodeErr = auto()

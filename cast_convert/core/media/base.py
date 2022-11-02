from __future__ import annotations

import logging
from enum import StrEnum, auto
from typing import Any, Self, Type

from ..base import normalize_info
from ..parse import ALIAS_FMTS


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


class OnTranscodeErr(NormalizedFormat, StrEnum):
  cycle_video_encoders: str = auto()
  cycle_audio_encoders: str = auto()


def get_name(obj: Any) -> str:
  match obj:
    case type() as cls:
      return cls.__name__

    case _:
      return type(obj).__name__

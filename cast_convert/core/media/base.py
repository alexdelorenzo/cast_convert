from __future__ import annotations

import logging
from enum import StrEnum, auto
from typing import Self, Type

from ..base import get_name
from ..types import WithName
from ..fmt import normalize
from ..parse import ALIAS_FMTS


log = logging.getLogger(__name__)


class NormalizedFormat(WithName):
  unknown: Self | str

  def __bool__(self) -> bool:
    return self != self.unknown

  def __repr__(self) -> str:
    return f"{get_name(self)}({self})"

  @classmethod
  def _missing_(cls: Type[Self], value: str) -> Self:
    name = get_name(cls)
    log.info(f"[{name}] Missing: {value}")

    if alias := getattr(cls, value, None):
      log.info(f"[{name}] Using {alias} as an alias for {value}")
      return alias

    if alias := ALIAS_FMTS.get(value):
      log.info(f"[{name}] Using {alias} as an alias for {value}")
      return cls(alias)

    log.info(f"[{name}] Not found, using `unknown` instead of {value}")
    return cls.unknown

  @classmethod
  def from_info(cls: Type[Self], info: str | None) -> Self:
    name = get_name(cls)

    if not info:
      log.info(f"[{name}] no info supplied: {info}")
      return cls.unknown

    if not isinstance(info, str):
      raise TypeError(f"[{name}] Can't normalize: {info}")

    normalized = normalize(info)
    log.debug(f'{name}({info}) normalized as {name}({normalized})')

    return cls(normalized)


class OnTranscodeErr(NormalizedFormat, StrEnum):
  cycle_video_encoders: OnTranscodeErr = auto()
  cycle_audio_encoders: OnTranscodeErr = auto()

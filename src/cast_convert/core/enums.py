from __future__ import annotations

from enum import IntEnum, StrEnum, auto
from typing import Self


class LogLevel(StrEnum):
  debug = auto()
  info = auto()
  warn = auto()
  error = auto()
  critical = auto()
  fatal = auto()


class Strategy(StrEnum):
  quit = auto()
  skip = auto()
  force = auto()


class Rc(IntEnum):
  """Return codes"""
  ok: Self = 0
  err = auto()

  no_command = auto()
  missing_args = auto()
  no_matching_device = auto()

  must_convert = auto()
  failed_conversion = auto()
  unknown_format = auto()

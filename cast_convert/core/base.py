from __future__ import annotations

from typing import (
  Final, Iterable, TypeVar,
  Callable,
)
from decimal import Decimal
import logging


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
Resolution = int

DEFAULT_VIDEO_FPS: Final[Fps] = Fps()
DEFAULT_VIDEO_LEVEL: Final[Level] = Level()

DEFAULT_PROFILE_FPS: Final[Fps] = Fps('24.0')
DEFAULT_PROFILE_LEVEL: Final[Level] = Level('0.0')
DEFAULT_PROFILE_RESOLUTION: Final[Resolution] = 720


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

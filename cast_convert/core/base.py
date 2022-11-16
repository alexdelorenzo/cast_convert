from __future__ import annotations

from decimal import Decimal
from enum import IntEnum
from typing import (
  Callable, Final, Iterable, Protocol, TYPE_CHECKING, TypeVar
)


if TYPE_CHECKING:
  from .media.formats import Metadata


DEFAULT_MODEL: Final[str] = 'Chromecast 1st Gen'

AT: Final[str] = '@'
LEVEL_SEP: Final[str] = 'L'
PROFILE_SEP: Final[str] = AT + LEVEL_SEP
SUBTITLE_SEP: Final[str] = '/'


T = TypeVar('T')
U = TypeVar('U')

Item = T | U | None


class Decimal(Decimal):
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

DESCRIPTION: Final[str] = \
  "📽️ Identify and convert videos to formats that are Chromecast supported."


class Rc(IntEnum):
  """Return codes"""
  ok: int = 0
  err: int = 1

  missing_args: int = 2
  no_matching_device: int = 3

  must_convert: int = 4


class IsCompatible(Protocol):
  def is_compatible(self, other: Metadata) -> bool:
    pass


class AsDict(Protocol):
  @property
  def as_dict(self) -> dict[str, Metadata]:
    pass


class AsText(Protocol):
  @property
  def text(self) -> str:
    pass


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



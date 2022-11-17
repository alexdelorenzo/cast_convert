from __future__ import annotations

import logging
from decimal import Decimal
from enum import IntEnum, StrEnum, auto
from functools import cache
from multiprocessing import cpu_count
from pathlib import Path
from typing import (
  Any, Callable, Final, Iterable, Protocol, TYPE_CHECKING, TypeVar,
)

from more_itertools import peekable
from rich.logging import RichHandler
from rich.markup import escape
from rich import print
from thefuzz import process


if TYPE_CHECKING:
  from .media.formats import Metadata


DEFAULT_MODEL: Final[str] = 'Chromecast 1st Gen'
DEFAULT_REPLACE: Final[bool] = False
DEFAULT_JOBS: Final[int] = 2
DEFAULT_THREADS: Final[int] = cpu_count()

AT: Final[str] = '@'
TAB: Final[str] = '  '
LEVEL_SEP: Final[str] = 'L'
PROFILE_SEP: Final[str] = AT + LEVEL_SEP
SUBTITLE_SEP: Final[str] = '/'
NEW_LINE: Final[str] = '\n'
PRIVATE_PREFIX: Final[str] = '_'
JOIN_COMMAND: Final[str] = ' '

MIN_FUZZY_MATCH_SCORE: Final[int] = 30

FILESIZE_CHECK_WAIT: Final[float] = 2.0
NO_SIZE: Final[int] = -1


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
DEFAULT_PROFILE_RESOLUTION: Final[Resolution] = Resolution(720)

DESCRIPTION: Final[str] = \
  "📽️ Identify and convert videos to formats that are Chromecast supported."


Paths = set[Path]


class Levels(StrEnum):
  critical: Levels = auto()
  debug: Levels = auto()
  error: Levels = auto()
  fatal: Levels = auto()
  info: Levels = auto()
  warn: Levels = auto()


DEFAULT_LOG_LEVEL: Final[Levels] = Levels('warn')


class Rc(IntEnum):
  """Return codes"""
  ok: int = 0
  err: int = auto()

  no_command: int = auto()
  missing_args: int = auto()
  no_matching_device: int = auto()

  must_convert: int = auto()


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


class Peekable(peekable, Iterable[T]):
  """Generic and typed `peekable` with convenience methods."""
  iterable: Iterable[T]

  @property
  def is_empty(self) -> bool:
    return not self


def first(iterable: Iterable[T], default: Item = None) -> Item:
  iterator = iter(iterable)
  return next(iterator, default)


def normalize(
  text: str,
  condition: Callable[[str], bool] = str.isalnum,
  transform: Callable[[str], str] = lambda x: x,
) -> str:
  text = text.casefold()

  return ''.join(
    transform(char)
    for char in text
    if condition(char)
  )


def esc(text: str | Any) -> str:
  return escape(str(text))


def tab(text: str | Any, tabs: int = 1) -> str:
  indent: str = TAB * tabs

  if not isinstance(text, str):
    text: str = str(text)

  lines = text.split(NEW_LINE)

  return NEW_LINE.join(f'{indent}{line}' for line in lines)


def checklist(text: str | Any) -> str:
  if not isinstance(text, str):
    text: str = str(text)

  lines = text.split(NEW_LINE)

  return NEW_LINE.join(f'{TAB}- {line}' for line in lines)


def tab_list(
  text: str | Any,
  tabs: int = 1,
  out: bool = False,
) -> str:
  text: str = tab(checklist(text), tabs=tabs)

  if out:
    print(text)

  return text


def tabs(
  text: str | Any,
  tabs: int = 1,
  out: bool = False,
  tick: bool = False,
) -> str:
  if tick:
    text = checklist(text)

  text: str = tab(text, tabs=tabs)

  if out:
    print(text)

  return text


def setup_logging(log_level: Levels = DEFAULT_LOG_LEVEL):
  log_level = get_fuzzy_match(log_level, Levels, min_score=0)
  handlers = [RichHandler(rich_tracebacks=True)]

  logging.basicConfig(level=log_level.upper(), handlers=handlers)
  logging.debug(f'Set log level to {log_level}.')


def get_fuzzy_match(
  name: str,
  items: Iterable[T],
  min_score: int = MIN_FUZZY_MATCH_SCORE,
) -> T | None:
  closest, score = process.extractOne(name, items)

  if score < min_score:
    return None

  return closest

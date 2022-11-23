from __future__ import annotations

import logging
import sys
from collections.abc import Iterable
from decimal import Decimal
from enum import IntEnum, StrEnum, auto
from functools import wraps
from multiprocessing import cpu_count
from pathlib import Path
from types import FunctionType, MethodType
from typing import (
  Any, Callable, Final, ParamSpec, Protocol, Self,
  TYPE_CHECKING, TypeVar, runtime_checkable,
)

from more_itertools import peekable
from rich import print
from rich.logging import RichHandler
from rich.markup import escape
from thefuzz import process
from typer import Exit

from .exceptions import CannotCompare, UnknownFormat

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

NO_BIAS: Final[int] = 0
CODEC_BIAS: Final[int] = 5
INCREMENT: Final[int] = 1


class Decimal(Decimal):
  def __format__(self, *args, **kwargs) -> str:
    return str(self)

  def __repr__(self) -> str:
    return str(self)


@runtime_checkable
class HasName(Protocol):
  @property
  def name(self) -> str: ...


# Python 3.11 removed the ability to use @classmethod with @property
# see: https://stackoverflow.com/a/13624858
class classproperty(property):
  def __get__(self, instance: Self, owner: type[Self]) -> Any:
    return self.fget(owner)


class WithName:
  @classproperty
  def name(self: Self) -> str:
    if doc := self.__doc__:
      name, *_ = doc.split(NEW_LINE)
      return name

    return get_name(self)


class Fps(Decimal, WithName):
  """Frame rate"""

  def __str__(self) -> str:
    if self is VariableFps:
      return VFR_DESCRIPTION

    return super().__str__()


VariableFps: Final[Fps] = Fps('-1')
VFR_DESCRIPTION: Final[str] = 'Variable frame rate'


class Level(Decimal, WithName):
  """Encoder Level"""
  pass


class Resolution(int, WithName):
  """Resolution Height"""
  pass


DEFAULT_VIDEO_FPS: Final[Fps] = Fps()
DEFAULT_VIDEO_LEVEL: Final[Level] = Level()

DEFAULT_PROFILE_FPS: Final[Fps] = Fps('24.0')
DEFAULT_PROFILE_LEVEL: Final[Level] = Level('0.0')
DEFAULT_PROFILE_RESOLUTION: Final[Resolution] = Resolution(720)


class LogLevel(StrEnum):
  debug: Self = auto()
  info: Self = auto()
  warn: Self = auto()
  error: Self = auto()
  critical: Self = auto()
  fatal: Self = auto()


DEFAULT_LOG_LEVEL: Final[LogLevel] = LogLevel('warn')

T = TypeVar('T')
U = TypeVar('U')
P = ParamSpec('P')

Item = T | U | None

Paths = set[Path]

Decorated = Callable[P, T]
Decoratable = Callable[P, T]
Decorator = Callable[[Decoratable], Decorated]


class Strategy(StrEnum):
  quit: Self = auto()
  skip: Self = auto()


class Rc(IntEnum):
  """Return codes"""
  ok: Self = 0
  err: Self = auto()

  no_command: Self = auto()
  missing_args: Self = auto()
  no_matching_device: Self = auto()

  must_convert: Self = auto()
  failed_conversion: Self = auto()
  unknown_format: Self = auto()


@runtime_checkable
class IsCompatible(Protocol):
  def is_compatible(self, other: Metadata) -> bool:
    raise CannotCompare(f"Can't compare {self} with {other}")


@runtime_checkable
class AsDict(Protocol):
  @property
  def as_dict(self) -> dict[str, Metadata]: ...


@runtime_checkable
class AsText(Protocol):
  @property
  def text(self) -> str: ...


@runtime_checkable
class HasWeight(Protocol):
  @property
  def bias(self) -> int:
    return NO_BIAS

  @property
  def count(self) -> int: ...

  @property
  def weight(self) -> int: ...


@runtime_checkable
class HasItems(Protocol):
  def __bool__(self) -> bool:
    return has_items(self)


class Peekable(peekable, Iterable[T]):
  """Generic and typed `peekable` with convenience methods."""
  iterable: Iterable[T]

  @property
  def is_empty(self) -> bool:
    return not self


def has_items(obj: Any) -> bool:
  try:
    items = iter(obj)

  except TypeError as e:
    logging.warning(f"[{e}] Can't get an iterator for type {get_name(obj)}")
    items = obj.__dict__.values()

  return any(item is not None for item in items)


def handle_errors(*exceptions: type[Exception], strategy: Strategy = Strategy.quit) -> Decorator:
  def decorator(func: Decoratable) -> Decorated:
    @wraps(func)
    def decorated(*args: P.args, **kwargs: P.kwargs) -> T:
      try:
        return func(*args, **kwargs)

      except exceptions as e:
        logging.exception(e)
        logging.error(f'Failed: {func.__name__}({args=}, {kwargs=})')

        match strategy:
          case Strategy.quit:
            print(f'[b red]Quitting because of error:[/] {e}', file=sys.stderr)
            raise Exit(Rc.err) from e

          case Strategy.skip:
            logging.warning(f'[{strategy}] Encountered error: {e}, skipping.')

    return decorated

  return decorator


def get_error_handler(
  func: Decoratable,
  *exceptions: type[Exception],
  strategy: Strategy = Strategy.quit
) -> Decorated:
  error_handler = handle_errors(*exceptions, strategy=strategy)
  return error_handler(func)


bad_file_exit: Final[Decorator] = handle_errors(UnknownFormat)


def first(iterable: Iterable[T], default: Item = None) -> Item:
  iterator = iter(iterable)
  return next(iterator, default)


def identity(obj: T) -> T:
  return obj


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


def setup_logging(level: LogLevel = DEFAULT_LOG_LEVEL):
  handlers = [RichHandler(rich_tracebacks=True)]

  logging.basicConfig(level=level.upper(), handlers=handlers)


def get_fuzzy_match(
  name: str,
  items: Iterable[str],
  min_score: int = MIN_FUZZY_MATCH_SCORE,
) -> str | None:
  closest, score = process.extractOne(name, items)
  logging.debug(f"Fuzzy match: {name} -> {closest} ({score})")

  if score < min_score:
    return None

  return closest


def get_name(obj: Any) -> str:
  match obj:
    case type() as cls:
      return cls.__name__

    case (FunctionType() | MethodType()) as func:
      return func.__name__

    case has_name if name := getattr(has_name, '__name__', None):
      return name

    case _:
      return type(obj).__name__

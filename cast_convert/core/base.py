from __future__ import annotations

import logging
import sys
from abc import abstractmethod
from collections.abc import Iterable
from decimal import Decimal
from enum import IntEnum, StrEnum, auto
from functools import total_ordering, wraps
from multiprocessing import cpu_count
from pathlib import Path
from types import FunctionType, MethodType
from typing import (Any, Callable, Final, NamedTuple, Protocol, Self, TYPE_CHECKING, override, runtime_checkable)

from more_itertools import peekable
from rich import print
from rich.logging import RichHandler
from thefuzz import process
from typer import Exit

from .exceptions import CannotCompare, UnknownFormat


RESOLUTION_SEP = 'x'

if TYPE_CHECKING:
  from .media.formats import Metadata


log = logging.getLogger(__name__)

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
  @override
  def __format__(self, *args, **kwargs) -> str:
    return str(self)

  @override
  def __repr__(self) -> str:
    return str(self)


# Python 3.11 removed the ability to use @classmethod with @property
# see: https://stackoverflow.com/a/13624858
class classproperty(property):
  def __get__(self: Self, instance: Self, owner: type[Self]) -> Any:
    return self.fget(owner)


def with_name(self: Self) -> str:
  if doc := self.__doc__:
    name, *_ = doc.split(NEW_LINE)
    return name

  return get_name(self)


type NameMethod = Callable[[Self], str]


class WithName:
  name: NameMethod = classproperty(with_name)


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


# @total_ordering
class Height(int, WithName):
  """Resolution Height"""

  def is_compatible(self, other: Self) -> bool:
    return self >= other


# @total_ordering
class Width(int, WithName):
  """Resolution Height"""

  def is_compatible(self, other: Self) -> bool:
    return self >= other


type Components = Width | Height | int | float


# @total_ordering
class Resolution(NamedTuple):
  """Resolution"""

  width: Width
  height: Height

  def __lt__(self, other: Self | Components | Any) -> bool:
    match other:
      case Resolution(width, height):
        return self.width < width or self.height < height

      case Height(height) | int(height) | float(height):
        return self.height < height

      case Width(width) | int(width) | float(width):
        return self.width < width

      case _:
        raise ValueError(f"Can't compare with {other}")

  def __eq__(self, other: Self | Components | Any) -> bool:
    match other:
      case Resolution(width, height):
        return self.width == width and self.height == height

      case Height(height) | int(height) | float(height):
        return self.height == height

      case Width(width) | int(width) | float(width):
        return self.width == width

      case _:
        raise ValueError(f"Can't compare with {other}")

  def __str__(self) -> str:
    return f"{self.width}{RESOLUTION_SEP}{self.height}"

  @classproperty
  def name(cls: type[Self]) -> str:
    return with_name(cls)

  @classmethod
  def from_str(cls: type[Self], text: str) -> Self:
    width, height = text.split(RESOLUTION_SEP)
    return cls.new(width, height)

  @classmethod
  def new(cls: type[Self], width: int = 0, height: int = 0) -> Self:
    return cls(Width(width), Height(height))

  def is_compatible(self, other: Resolution) -> bool:
    return self >= other


DEFAULT_VIDEO_FPS: Final[Fps] = Fps()
DEFAULT_VIDEO_LEVEL: Final[Level] = Level()

DEFAULT_PROFILE_FPS: Final[Fps] = Fps('24.0')
DEFAULT_PROFILE_LEVEL: Final[Level] = Level('0.0')
DEFAULT_PROFILE_RESOLUTION: Final[Resolution] = Resolution(Width(1280), Height(720))


class LogLevel(StrEnum):
  debug = auto()
  info = auto()
  warn = auto()
  error = auto()
  critical = auto()
  fatal = auto()


DEFAULT_LOG_LEVEL: Final[LogLevel] = LogLevel.warn


type Item[T, U] = T | U | None
type Paths = set[Path]

type Decorated[**P, T] = Callable[P, T]
type Decoratable[**P, T] = Callable[P, T]
type Decorator[**P, T] = Callable[[Decoratable], Decorated]


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


@runtime_checkable
class HasName(Protocol):
  name: str


@runtime_checkable
class IsCompatible(Protocol):
  def is_compatible(self, other: Metadata) -> bool:
    raise CannotCompare(f"Can't compare {self} with {other}")


@runtime_checkable
class AsDict(Protocol):
  @property
  @abstractmethod
  def as_dict(self) -> dict[str, Metadata]: ...


@runtime_checkable
class AsText(Protocol):
  @property
  @abstractmethod
  def text(self) -> str: ...


@runtime_checkable
class HasWeight(Protocol):
  @property
  def bias(self) -> int:
    return NO_BIAS

  @property
  @abstractmethod
  def count(self) -> int: ...

  @property
  @abstractmethod
  def weight(self) -> int: ...


@runtime_checkable
class HasItems(Protocol):
  def __bool__(self) -> bool:
    return has_items(self)


class Peekable[T](peekable, Iterable[T]):
  """Generic and typed `peekable` with convenience methods."""
  iterable: Iterable[T]

  @property
  def is_empty(self) -> bool:
    return not self


def has_items(obj: Any) -> bool:
  try:
    items = iter(obj)

  except TypeError as e:
    log.warning(f"[{e}] Can't get an iterator for type {get_name(obj)}")
    items = obj.__dict__.values()

  return any(item is not None for item in items)


def handle_errors(*exceptions: type[Exception], strategy: Strategy = Strategy.quit) -> Decorator:
  def decorator[**P, T](func: Decoratable) -> Decorated:
    @wraps(func)
    def decorated(*args: P.args, **kwargs: P.kwargs) -> T:
      try:
        return func(*args, **kwargs)

      except exceptions as e:
        log.exception(e)
        log.error(f'Failed: {get_name(func)}({args=}, {kwargs=})')

        match strategy:
          case Strategy.quit:
            print(f'[b red]Quitting because of error:[/] {e}', file=sys.stderr)
            raise Exit(Rc.err) from e

          case Strategy.skip:
            log.warning(f'[{strategy}] Encountered error: {e}, skipping.')

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


def first[T](iterable: Iterable[T], default: Item = None) -> Item:
  iterator = iter(iterable)
  return next(iterator, default)


def identity[T](obj: T) -> T:
  return obj


def setup_logging(level: LogLevel = DEFAULT_LOG_LEVEL):
  handlers = [RichHandler(rich_tracebacks=True)]

  logging.basicConfig(level=level.upper(), handlers=handlers)


def get_fuzzy_match(
  name: str,
  items: Iterable[str],
  min_score: int = MIN_FUZZY_MATCH_SCORE,
) -> str | None:
  closest, score = process.extractOne(name, items)
  log.debug(f"Fuzzy match: {name} -> {closest} ({score})")

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

    case HasName() as has_name:
      return has_name.name

    case _:
      return type(obj).__name__

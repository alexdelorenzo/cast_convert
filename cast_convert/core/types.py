from __future__ import annotations

import logging
from decimal import Decimal
from functools import total_ordering
from pathlib import Path
from types import FunctionType, MethodType
from typing import Any, Callable, Final, Iterable, NamedTuple, Protocol, Self, override, runtime_checkable

from more_itertools import peekable

from .exceptions import CannotCompare
from .protocols import HasName


type Components = Width | Height | int | float
type NameMethod = Callable[[Self], str]
type Item[T, U] = T | U | None

type Decorated[**P, T] = Callable[P, T]
type Decoratable[**P, T] = Callable[P, T]
type Decorator[**P, T] = Callable[[Decoratable], Decorated]


log = logging.getLogger(__name__)

RESOLUTION_SEP: Final[str] = 'x'
VFR_DESCRIPTION: Final[str] = 'Variable frame rate'


Paths = set[Path]


class FormattedDecimal(Decimal):
  @override
  def __format__(self, *args, **kwargs) -> str:
    return str(self)

  @override
  def __repr__(self) -> str:
    return str(self)


class classproperty(property):
  def __get__(self: Self, instance: Self, owner: type[Self]) -> Any:
    return self.fget(owner)


def with_name(self: Self) -> str:
  if doc := self.__doc__:
    name, *_ = doc.split('\n')
    return name

  return get_name(self)


class WithName:
  name: NameMethod = classproperty(with_name)


class Fps(FormattedDecimal, WithName):
  """Frame rate"""

  def __str__(self) -> str:
    if self is VariableFps:
      return VFR_DESCRIPTION

    return super().__str__()


@total_ordering
class Resolution(NamedTuple):
  """Resolution"""

  width: Width
  height: Height

  @override
  def __eq__(self, other: Self | Components | Any) -> bool:
    match other:
      case Resolution(width, height):
        return self.width == width and self.height == height

      case Height(height) | int(height) | float(height):
        return self.height == height

      case Width(width) | int(width) | float(width):
        return self.width == width

      case _:
        raise CannotCompare(f"Can't compare {self!r} with {other}")

  @override
  def __lt__(self, other: Self | Components | Any) -> bool:
    match other:
      case Resolution(width, height):
        return self.width < width or self.height < height

      case Height(height) | int(height) | float(height):
        return self.height < height

      case Width(width) | int(width) | float(width):
        return self.width < width

      case _:
        raise CannotCompare(f"Can't compare {self!r} with {other}")

  def __str__(self) -> str:
    return RESOLUTION_SEP.join(map(str, self))

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


class Peekable[T](peekable, Iterable[T]):
  """Generic and typed `peekable` with convenience methods."""
  iterable: Iterable[T]

  @property
  def is_empty(self) -> bool:
    return not self


class Level(FormattedDecimal, WithName):
  """Encoder Level"""
  pass


class Height(int, WithName):
  """Resolution Height"""

  def is_compatible(self, other: Self) -> bool:
    return self >= other


class Width(int, WithName):
  """Resolution Height"""

  def is_compatible(self, other: Self) -> bool:
    return self >= other


@runtime_checkable
class HasItems(Protocol):
  def __bool__(self) -> bool:
    return has_items(self)


VariableFps: Final[Fps] = Fps('-1')
DEFAULT_VIDEO_FPS: Final[Fps] = Fps()
DEFAULT_PROFILE_FPS: Final[Fps] = Fps('24.0')

DEFAULT_VIDEO_LEVEL: Final[Level] = Level()
DEFAULT_PROFILE_LEVEL: Final[Level] = Level('0.0')

DEFAULT_PROFILE_RESOLUTION: Final[Resolution] = Resolution(Width(1280), Height(720))


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


def has_items(obj: Any) -> bool:
  try:
    items = iter(obj)

  except TypeError as e:
    log.warning(f"[{e}] Can't get an iterator for type {get_name(obj)}")
    items = obj.__dict__.values()

  return any(item is not None for item in items)

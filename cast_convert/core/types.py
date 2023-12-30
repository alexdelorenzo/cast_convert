from __future__ import annotations

import logging
from collections.abc import Hashable
from decimal import Decimal
from functools import total_ordering
from pathlib import Path
from typing import Any, Callable, Final, Iterable, NamedTuple, Self, override

from more_itertools import peekable

from .exceptions import CannotCompare
from .protocols import IsCompatible, get_name


RESOLUTION_SEP: Final[str] = 'x'
DOCSTRING_NAME_SEP: Final[str] = '\n'
VFR_DESCRIPTION: Final[str] = 'Variable frame rate'


type Components = Width | Height | int | float
type NameMethod = Callable[[Self], str]
type Item[T, U] = T | U | None

type Decoratable[**P, T] = Callable[P, T]
type Decorated[**P, T] = Callable[P, T]
type Decorator[**P, T] = Callable[[Decoratable], Decorated]

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
    name, *_ = doc.split(DOCSTRING_NAME_SEP)
    return name.strip()

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
      case width, height:
        return self.width == width and self.height == height

      case Height(height):
        return self.height == height

      case Width(width):
        return self.width == width

      case _:
        raise CannotCompare(f"Can't compare {self!r} with {other}")

  @override
  def __lt__(self, other: Self | Components | Any) -> bool:
    match other:
      case width, height:
        return self.width < width and self.height < height

      case Height(height):
        return self.height < height

      case Width(width):
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
  def new(cls: type[Self], width: int | str = 0, height: int | str = 0) -> Self:
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


@total_ordering
class Component(int, Hashable, IsCompatible, WithName):
  @override
  def __eq__(self, other: Self | Resolution) -> bool:
    match self, other:
      case Height(height), Height(other):
        return height == int(other)

      case Width(width), Width(other):
        return width == int(other)

      case Height(height), Resolution(_, int(other)):
        return height == other

      case Width(width), Resolution(int(other), _):
        return width == other

      case Width(), Height() | Height(), Width():
        raise CannotCompare(f"Can't compare Height with Width")

      case int(this), int(other):
        return int(this) == int(other)

      case _:
        raise CannotCompare(f"Can't compare {self!r} with {other}")

  @override
  def __lt__(self, other: Self | Resolution) -> bool:
    match self, other:
      case Height(height), Height(other):
        return height < int(other)

      case Width(width), Width(other):
        return width < int(other)

      case Height(height), Resolution(_, int(other)):
        return height < other

      case Width(width), Resolution(int(other), _):
        return width < other

      case Width(), Height() | Height(), Width():
        raise CannotCompare(f"Can't compare Height with Width")

      case int(this), int(other):
        return int(this) < int(other)

      case _:
        raise CannotCompare(f"Can't compare {self!r} with {other}")

  @override
  def __hash__(self):
    return super().__hash__()

  def is_compatible(self, other: Self) -> bool:
    return self >= other


class Height(Component):
  """Resolution Height"""


class Width(Component):
  """Resolution Width"""


VariableFps: Final[Fps] = Fps('-1')
DEFAULT_VIDEO_FPS: Final[Fps] = Fps()
DEFAULT_PROFILE_FPS: Final[Fps] = Fps('24.0')

DEFAULT_VIDEO_LEVEL: Final[Level] = Level()
DEFAULT_PROFILE_LEVEL: Final[Level] = Level('0.0')

DEFAULT_PROFILE_RESOLUTION: Final[Resolution] = Resolution(Width(1280), Height(720))

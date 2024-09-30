from __future__ import annotations

import logging
from abc import abstractmethod
from types import FunctionType, MethodType
from typing import Any, Final, Protocol, runtime_checkable, TYPE_CHECKING

from .exceptions import CannotCompare

if TYPE_CHECKING:
  from .media.formats import Metadata


log = logging.getLogger(__name__)

NO_BIAS: Final[int] = 0


@runtime_checkable
class HasName(Protocol):
  name: str


@runtime_checkable
class IsCompatible(Protocol):
  def is_compatible(self, other: Metadata) -> bool:
    raise CannotCompare(f"Can't compare {self=!r} with {other!r}")


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


def has_items(obj: Any) -> bool:
  try:
    items = iter(obj)

  except TypeError as e:
    log.warning(f"[{e}] Can't get an iterator for type {get_name(obj)}")
    items = obj.__dict__.values()

  return any(item is not None for item in items)


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

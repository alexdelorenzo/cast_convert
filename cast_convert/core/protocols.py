from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any, Final, Protocol, runtime_checkable, TYPE_CHECKING

from .exceptions import CannotCompare
from .types import get_name, log


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

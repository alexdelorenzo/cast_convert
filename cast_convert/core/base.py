from __future__ import annotations

import logging
import sys
from collections.abc import Iterable
from functools import wraps
from multiprocessing import cpu_count
from typing import (Final, TYPE_CHECKING)

from rich import print
from rich.logging import RichHandler
from thefuzz import process
from typer import Exit

from .enums import LogLevel, Rc, Strategy
from .exceptions import UnknownFormat
from .types import Decoratable, Decorated, Decorator, Item, get_name


if TYPE_CHECKING:
  pass


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

CODEC_BIAS: Final[int] = 5
INCREMENT: Final[int] = 1


DEFAULT_LOG_LEVEL: Final[LogLevel] = LogLevel.warn


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
            log.warning(f'[{strategy=}] Encountered error: {e}, skipping.')

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



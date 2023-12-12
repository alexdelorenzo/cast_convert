from __future__ import annotations

from typing import Any, Callable

from rich import print
from rich.markup import escape

from .base import NEW_LINE, TAB, identity


def normalize(
  text: str,
  condition: Callable[[str], bool] = str.isalnum,
  transform: Callable[[str], str] = identity,
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


def tabs(text: str | Any, tabs: int = 1, out: bool = False, tick: bool = False) -> str:
  if tick:
    text = checklist(text)

  text: str = tab(text, tabs=tabs)

  if out:
    print(text)

  return text

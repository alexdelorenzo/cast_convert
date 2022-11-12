from __future__ import annotations

import logging
from asyncio import run
from pathlib import Path
from typing import Final, NoReturn

from typer import Typer, Option, Argument, Exit, Context
from rich import print

from ..core.base import DEFAULT_MODEL, DESCRIPTION
from ..core.convert.watch import DEFAULT_PROCS, convert_videos
from ..core.convert.helpers import _convert, _get_command, _inspect, show_devices
from ..core.model.device import get_devices_from_file
from ..core.model.video import Video


RC_MISSING_ARGS: Final[int] = 1

DEFAULT_NAME_OPT: Final[Option] = Option(
  default=DEFAULT_MODEL,
  help='Chromecast model name',
)

DEFAULT_PATHS_ARG: Final[Argument] = Argument(
  default=...,
  help='Path, or paths, to video(s)',
  resolve_path=True,

)

app: Final[Typer] = Typer()


def check_paths(paths: list[Path]) -> NoReturn | None:
  if not paths:
    print('[b red]No paths supplied.')
    raise Exit(code=RC_MISSING_ARGS)


@app.command()
def get_command(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
):
  """
  Get FFMPEG transcoding command.
  """
  check_paths(paths)

  for path in paths:
    _get_command(name, path)


@app.command()
def convert(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
):
  """
  Convert video for Chromecast compatibility.
  """
  check_paths(paths)

  for path in paths:
    _convert(name, path)


@app.command()
def inspect(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
):
  """
  Inspect a video to see what attributes should be decoded.
  """
  check_paths(paths)

  for path in paths:
    _inspect(name, path)


@app.command()
def devices():
  """
  List all supported device names.
  """
  _devices = get_devices_from_file()

  print('You can use these device names with the [b]--name[/b] flag:')
  show_devices(_devices)


@app.command()
def watch(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  threads: int = DEFAULT_PROCS,
):
  """
  Watch directories for added videos and convert them.
  """
  check_paths(paths)

  coro = convert_videos(*paths, device=name, procs=threads)
  run(coro)


@app.callback(help=DESCRIPTION)
def main(
  ctx: Context,
  log_level: int = Option(logging.WARN, help="Choose level of debug logging, 0 to 50"),
):
  logging.basicConfig(level=log_level)

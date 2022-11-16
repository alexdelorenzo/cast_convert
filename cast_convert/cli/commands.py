from __future__ import annotations

import logging
from asyncio import run
from pathlib import Path
from typing import Final

from click.exceptions import Exit
from typer import Typer, Option, Argument, Context
from rich import print

from ..core.base import DEFAULT_MODEL, DESCRIPTION, Rc
from ..core.convert.watch import DEFAULT_JOBS, DEFAULT_THREADS, convert_videos

from ..core.convert.helpers import _convert, _get_command, _inspect, show_devices
from ..core.model.device import get_devices_from_file


DEFAULT_NAME_OPT: Final[Option] = Option(
  default=DEFAULT_MODEL,
  help='Device model name',
)

DEFAULT_PATHS_ARG: Final[Argument] = Argument(
  default=...,
  help='Path(s) to video(s)',
  resolve_path=True,
)

DEFAULT_THREADS_OPT: Final[Option] = Option(
  default=DEFAULT_THREADS,
  help="Number of threads to tell FFMPEG to use per job"
)


app: Final[Typer] = Typer()


@app.command()
def get_command(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  threads: int = DEFAULT_THREADS_OPT,
):
  """
  📜 Get FFMPEG transcoding command.
  """
  rc: int = Rc.ok

  for path in paths:
    if _get_command(name, path, threads):
      rc = Rc.must_convert

  raise Exit(code=rc)


@app.command()
def convert(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  threads: int = DEFAULT_THREADS_OPT,
):
  """
  📼 Convert video for Chromecast compatibility.
  """
  for path in paths:
    _convert(name, path, threads)


@app.command()
def inspect(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
):
  """
  🔎 Inspect a video to see what attributes should be decoded.
  """
  rc: int = Rc.ok

  for path in paths:
    if _inspect(name, path):
      rc = Rc.must_convert

  raise Exit(code=rc)


@app.command()
def devices():
  """
  📺 List all supported device names.
  """
  _devices = get_devices_from_file()

  print('You can use these device names with the [b]--name[/b] flag:')
  show_devices(_devices)


@app.command()
def watch(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  jobs: int = Option(DEFAULT_JOBS, help="Number of simultaneous transcoding jobs"),
  threads: int = DEFAULT_THREADS_OPT,
):
  """
  👀 Watch directories for added videos and convert them.
  """
  coro = convert_videos(*paths, device=name, jobs=jobs, threads=threads)
  run(coro)


@app.callback(help=DESCRIPTION)
def main(
  ctx: Context,
  log_level: str = Option('warn', help="Set the minimum logging level"),
):
  log_level = log_level.upper()
  logging.basicConfig(level=log_level)

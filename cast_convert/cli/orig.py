from __future__ import annotations

from pathlib import Path
from typing import Final, NoReturn

from typer import Typer, Option, Argument, Exit
from rich import print

from ..core.model.device import Device
from .helpers import DEFAULT_MODEL, _convert, _get_command, _inspect, show_devices


RC_MISSING_ARGS: Final[int] = 1

DEFAULT_NAME_OPT: Final[Option] = Option(
  default=DEFAULT_MODEL,
  help='Chromecast model name',
)


DEFAULT_PATHS_ARG: Final[Argument] = Argument(
  default=None,
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

  devices: tuple[Device] = tuple(Device.from_yaml())  # type: ignore

  print('You can use these device names with the [b]--name[/b] flag: ')
  show_devices(devices)





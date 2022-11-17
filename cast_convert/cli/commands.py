from __future__ import annotations

from asyncio import run
from enum import StrEnum
from pathlib import Path
from typing import Final

from rich import print
from typer import Argument, Context, Exit, Option, Typer

from .helpers import _get_command, _inspect, show_devices
from .. import COPYRIGHT_NOTICE, PROJECT_HOME, __version__
from ..core.base import DEFAULT_JOBS, DEFAULT_LOG_LEVEL, DEFAULT_MODEL, \
  DEFAULT_THREADS, DESCRIPTION, Levels, Rc, setup_logging
from ..core.convert.run import convert_from_name_path
from ..core.convert.watch import convert_videos
from ..core.model.device import get_devices_from_file


class Panels(StrEnum):
  about: str = "❓ About"
  analyze: str = '📊 Analyze'
  convert: str = '📽️ Convert'
  device: str = '📺 Device'
  encoder_options: str = '🖥 Encoder Options'
  supported: str = "🛠️ Hardware Support"


DEFAULT_NAME_OPT: Final[Option] = Option(
  DEFAULT_MODEL,
  '--name', '-n',
  help='📛 Device model name',
  rich_help_panel=Panels.device,
)

DEFAULT_PATHS_ARG: Final[Argument] = Argument(
  default=...,
  help='Path(s) to video(s).',
  resolve_path=True,
  metavar='📂PATHS',
  show_default=False,
)

DEFAULT_REPLACE_OPT: Final[Option] = Option(
  False,
  '--replace', '-r',
  help='💾 Replace original file with transcoded video.',
  rich_help_panel=Panels.encoder_options,
  show_default=True,
)

DEFAULT_THREADS_OPT: Final[Option] = Option(
  DEFAULT_THREADS,
  '--threads', '-t',
  help="🧵 Number of threads to tell FFMPEG to use per job.",
  rich_help_panel=Panels.encoder_options,
)

LONG_DESCRIPTION: Final[str] = f"""
{DESCRIPTION}

\n\t
  See [b]{PROJECT_HOME}[/b] for more information.
  {COPYRIGHT_NOTICE}.
"""


cli: Final[Typer] = Typer(
  no_args_is_help=True,
  help=LONG_DESCRIPTION,
  rich_markup_mode='rich',
)


@cli.command(
  rich_help_panel=Panels.analyze,
  no_args_is_help=True,
)
def command(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  replace: bool = DEFAULT_REPLACE_OPT,
  threads: int = DEFAULT_THREADS_OPT,
):
  """
  📜 Get FFmpeg transcoding command.
  """
  rc: int = Rc.ok

  for path in paths:
    if _get_command(name, path, replace, threads):
      rc = Rc.must_convert

  raise Exit(rc)


@cli.command(
  rich_help_panel=Panels.convert,
  no_args_is_help=True,
)
def convert(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  replace: bool = DEFAULT_REPLACE_OPT,
  threads: int = DEFAULT_THREADS_OPT,
):
  """
  📼 Convert videos so they're compatible with specified device.
  """
  rc: int = Rc.ok

  for path in paths:
    if not convert_from_name_path(name, path, replace, threads):
      rc = Rc.err

  raise Exit(rc)


@cli.command(
  rich_help_panel=Panels.analyze,
  no_args_is_help=True,
)
def inspect(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
):
  """
  🔎 Inspect videos to see what attributes should get transcoded.
  """
  rc: int = Rc.ok

  for path in paths:
    if _inspect(name, path):
      rc = Rc.must_convert

  raise Exit(rc)


@cli.command(
  rich_help_panel=Panels.supported,
  # no_args_is_help=True,
)
def devices(
  details: bool = Option(
    False,
    '--details', '-d',
    help=":information: Show detailed device information.",
    rich_help_panel=Panels.device
  )
):
  """
  📺 List all supported devices.
  """
  _devices = get_devices_from_file()

  print('You can use these device names with the [b]--name[/b] flag:')
  show_devices(_devices, details)


@cli.command(
  rich_help_panel=Panels.convert,
  no_args_is_help=True,
)
def watch(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  jobs: int = Option(
    DEFAULT_JOBS,
    '--jobs', '-j',
    help=":input_numbers: Number of simultaneous transcoding jobs.",
    rich_help_panel=Panels.encoder_options
  ),
  replace: bool = DEFAULT_REPLACE_OPT,
  threads: int = DEFAULT_THREADS_OPT,
):
  """
  👀 Watch directories for new or modified videos and convert them.
  """
  coro = convert_videos(
    *paths,
    device=name,
    jobs=jobs,
    replace=replace,
    threads=threads
  )
  run(coro)


@cli.callback(
  invoke_without_command=True,
  no_args_is_help=True,
  # help=DESCRIPTION,
  # epilog=EPILOG,
)
def main(
  ctx: Context,
  log_level: Levels = Option(
    DEFAULT_LOG_LEVEL,
    '--log-level', '-l',
    help="🪵 Set the minimum logging level.",
    show_default=True,
    rich_help_panel=Panels.about,
  ),
  version: bool = Option(
    False,
    '--version', '-v',
    help="🔢 Show application version and quit.",
    rich_help_panel=Panels.about,
  ),
):
  setup_logging(log_level)

  if version:
    print(f'v{__version__}')
    raise Exit(Rc.ok)

  if not ctx.invoked_subcommand:
    print('[b red]You need to supply a command.')
    raise Exit(Rc.no_command)

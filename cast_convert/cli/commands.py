from __future__ import annotations

from asyncio import run
from enum import StrEnum
from pathlib import Path
from typing import Final

from rich import print
from typer import Argument, Context, Exit, Option, Typer
from typer.models import ArgumentInfo, OptionInfo

from .helpers import _get_command, _inspect, inspect_directory, show_devices
from .. import CLI_ENTRY, COPYRIGHT_NOTICE, DESCRIPTION, LICENSE, PROJECT_HOME, __version__
from ..core.base import DEFAULT_JOBS, DEFAULT_LOG_LEVEL, DEFAULT_MODEL, \
  DEFAULT_THREADS, bad_file_exit, setup_logging
from ..core.enums import LogLevel, Rc, Strategy

from ..core.convert.run import convert_paths
from ..core.convert.watch import convert_videos
from ..core.model.device import get_devices_from_file


THREAD_COUNT: Final[int] = max(int(DEFAULT_THREADS / DEFAULT_JOBS), 1)


class Panels(StrEnum):
  about = "❓ About"
  analyze = '📊 Analyze'
  convert = '📽️ Convert'
  device = '📺 Device'
  encoder_options = '🖥 Encoder Options'
  supported = "🛠️ Hardware Support"


DEFAULT_NAME_OPT: Final[OptionInfo] = Option(
  DEFAULT_MODEL,
  '--name', '-n',
  help='📛 Device model name',
  rich_help_panel=Panels.device,
)

DEFAULT_PATHS_ARG: Final[ArgumentInfo] = Argument(
  default=...,
  help='Path(s) to video(s).',
  resolve_path=True,
  metavar='📂PATHS',
  show_default=False,
)

DEFAULT_REPLACE_OPT: Final[OptionInfo] = Option(
  False,
  '--replace', '-r',
  help='💾 Replace original file with transcoded video.',
  rich_help_panel=Panels.encoder_options,
  show_default=True,
)

DEFAULT_THREADS_OPT: Final[OptionInfo] = Option(
  THREAD_COUNT,
  '--threads', '-t',
  help="🧵 Number of threads to tell FFMPEG to use per job.",
  rich_help_panel=Panels.encoder_options,
)

DEFAULT_JOBS_OPT: Final[OptionInfo] = Option(
  DEFAULT_JOBS,
  '--jobs', '-j',
  help=":input_numbers: Number of simultaneous transcoding jobs.",
  rich_help_panel=Panels.encoder_options
)

DEFAULT_LOG_OPT: Final[OptionInfo] = Option(
  DEFAULT_LOG_LEVEL,
  '--log-level', '-l',
  help="🪵 Set the minimum logging level.",
  show_default=True,
  rich_help_panel=Panels.about,
)

DEFAULT_STRATEGY_OPT: Final[OptionInfo] = Option(
  Strategy.quit,
  '--error', '-e',
  help="❗ Set the error handling strategy.",
  show_default=True,
  rich_help_panel=Panels.analyze,
)

DEFAULT_VERSION_OPT: Final[OptionInfo] = Option(
  False,
  '--version', '-v',
  help="🔢 Show application version and quit.",
  rich_help_panel=Panels.about,
)

DEFAULT_DETAILS_OPT: Final[OptionInfo] = Option(
  False,
  '--details', '-d',
  help=":information: Show detailed device information.",
  rich_help_panel=Panels.device
)

DEFAULT_SUBTITLE_OPT: Final[ArgumentInfo] = Option(
  None,
  '--subtitle', '-s',
  help='Path to subtitle file to embed.',
  resolve_path=True,
  show_default=False,
  rich_help_panel=Panels.encoder_options,
)

LONG_DESCRIPTION: Final[str] = f"""
{DESCRIPTION}

\n\t
  See [b]{PROJECT_HOME}[/b] for more information.
  {COPYRIGHT_NOTICE}. License: {LICENSE}
"""

cli: Final[Typer] = Typer(
  no_args_is_help=True,
  help=LONG_DESCRIPTION,
  rich_markup_mode='rich',
  name=CLI_ENTRY
)


@cli.command(
  rich_help_panel=Panels.analyze,
  no_args_is_help=True,
)
@bad_file_exit
def command(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  replace: bool = DEFAULT_REPLACE_OPT,
  threads: int = DEFAULT_THREADS_OPT,
  error: Strategy = DEFAULT_STRATEGY_OPT,
  subtitle: Path | None = DEFAULT_SUBTITLE_OPT,
):
  """
  📜 Get FFmpeg transcoding command.
  """
  rc: int = Rc.ok

  for path in paths:
    if _get_command(name, path, replace, threads, error, subtitle):
      rc = Rc.must_convert

  raise Exit(rc)


@cli.command(
  rich_help_panel=Panels.convert,
  no_args_is_help=True,
)
@bad_file_exit
def convert(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  replace: bool = DEFAULT_REPLACE_OPT,
  jobs: int = DEFAULT_JOBS_OPT,
  threads: int = DEFAULT_THREADS_OPT,
  error: Strategy = DEFAULT_STRATEGY_OPT,
  subtitle: Path | None = DEFAULT_SUBTITLE_OPT,
):
  """
  📼 Convert videos so that they're compatible with specified device.
  """
  coro = convert_paths(name, replace, threads, jobs, *paths, strategy=error, subtitle=subtitle)
  run(coro)


@cli.command(
  rich_help_panel=Panels.analyze,
  no_args_is_help=True,
)
@bad_file_exit
def inspect(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  error: Strategy = DEFAULT_STRATEGY_OPT,
):
  """
  🔎 Inspect videos to see what attributes should get transcoded.
  """
  rc: int = Rc.ok

  for path in paths:
    if path.is_dir():
      rc = inspect_directory(name, path, error) or rc

    elif _inspect(name, path, error):
      rc = Rc.must_convert

  raise Exit(rc)


@cli.command(
  rich_help_panel=Panels.supported,
  # no_args_is_help=True,
)
def devices(
  details: bool = DEFAULT_DETAILS_OPT,
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
@bad_file_exit
def watch(
  name: str = DEFAULT_NAME_OPT,
  paths: list[Path] = DEFAULT_PATHS_ARG,
  jobs: int = DEFAULT_JOBS_OPT,
  replace: bool = DEFAULT_REPLACE_OPT,
  threads: int = DEFAULT_THREADS_OPT,
  error: Strategy = DEFAULT_STRATEGY_OPT,
  subtitle: Path | None = DEFAULT_SUBTITLE_OPT,
):
  """
  👀 Watch directories for new or modified videos and convert them.
  """
  coro = convert_videos(
    *paths,
    device=name,
    jobs=jobs,
    replace=replace,
    threads=threads,
    error=error,
    subtitle=subtitle,
  )
  run(coro)


@cli.callback(
  invoke_without_command=True,
  no_args_is_help=True,
)
def main(
  ctx: Context,
  log_level: LogLevel = DEFAULT_LOG_OPT,
  version: bool = DEFAULT_VERSION_OPT,
):
  setup_logging(log_level)

  if version:
    print(f'v{__version__}')
    raise Exit(Rc.ok)

  if not ctx.invoked_subcommand:
    print('[b red]You need to supply a command.')
    raise Exit(Rc.no_command)

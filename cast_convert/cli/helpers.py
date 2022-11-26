from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable, AsyncIterable
from typing import Final

from aiopath import AsyncPath
from rich import print
from rich.markup import escape
from typer import Exit


from ..core.convert.run import get_ffmpeg_cmd, get_stream
from ..core.convert.transcode import should_transcode
from ..core.media.codecs import AudioCodec
from ..core.model.device import Device, Devices, get_device_fuzzy, get_devices_from_file
from ..core.model.video import Video
from ..core.base import DEFAULT_REPLACE, DEFAULT_THREADS, Peekable, Rc, Strategy, esc, \
  get_error_handler, tabs
from ..core.parse import DEVICE_INFO
from ..core.exceptions import UnknownFormat


GLOB_FILES_RECURSIVE: Final[str] = '**/*.*'


def show_devices(devices: Devices, details: bool = False):
  devices: Peekable[Device]

  for device in (devices := Peekable(devices)):
    tabs(f'[b]{device.name}', out=True, tick=True)

    if details:
      for profile in device.video_profiles:
        tabs(profile.codec, tabs=2, out=True, tick=True)
        tabs(profile.text, tabs=3, out=True, tick=True)

      tabs(AudioCodec.name, tabs=2, out=True, tick=True)
      for profile in device.audio_profiles:
        tabs(profile.codec, tabs=2, out=True, tick=True)
        tabs(profile.text, tabs=3, out=True, tick=True)

      if not devices.is_empty:
        print()


def _get_command(
  name: str,
  path: Path,
  replace: bool = DEFAULT_REPLACE,
  threads: int = DEFAULT_THREADS,
  error: Strategy = Strategy.quit,
) -> bool:
  video = Video.from_path(path)

  if not (device := _get_device_from_name(name)):
    raise Exit(Rc.no_matching_device)

  handled_inspector = get_error_handler(should_transcode, UnknownFormat, strategy=error)

  if not handled_inspector(device, video):
    return False

  formats = device.transcode_to(video)
  stream, _ = get_stream(video, formats, threads, replace)

  cmd = get_ffmpeg_cmd(stream, video.path)
  print(f'[b]{escape(cmd)}')

  return True


def _inspect(
  name: str,
  path: Path,
  error: Strategy = Strategy.quit
) -> bool:
  video = Video.from_path(path)

  if not (device := _get_device_from_name(name)):
    raise Exit(Rc.no_matching_device)

  handled_inspector = get_error_handler(should_transcode, UnknownFormat, strategy=error)

  if not handled_inspector(device, video):
    return False

  name = device.name

  print(f'[b red][❌️] Need to convert [b blue]"{esc(video.path)}"[/] to play on [yellow]{name}[/]...[/]')
  tabs('[b red]Must convert from:', out=True)
  tabs(video.formats.text, out=True, tick=True)

  tabs('[b green]To:', out=True)
  formats = device.transcode_to(video)
  tabs(formats.text, out=True, tick=True)

  return True


def _get_device_from_name(
  name: str,
  device_file: Path = DEVICE_INFO,
) -> Device | None:
  devices = get_devices_from_file(device_file)

  if not (dev := get_device_fuzzy(name, devices)):
    print(f'[b red][❌] Device name [yellow]"{name}"[/] not found[/], please use one of these:')
    show_devices(devices)

    return None

  return dev


def gen_paths(*paths: Path) -> Iterable[Path]:
  for path in paths:
    if path.is_dir():
      yield from path.glob(GLOB_FILES_RECURSIVE)
      continue

    yield path


async def gen_paths(*paths: Path) -> AsyncIterable[Path]:
  paths = map(AsyncPath, paths)

  for path in paths:
    if await path.is_dir():
      async for path in path.glob(GLOB_FILES_RECURSIVE):
        yield path

      continue

    yield path


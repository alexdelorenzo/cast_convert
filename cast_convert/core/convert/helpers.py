from __future__ import annotations

from pathlib import Path
from typing import Any, NoReturn

from click.exceptions import Exit
from rich import print

from .run import get_ffmpeg_cmd, get_stream, transcode_video
from .transcode import should_transcode
from ..base import Rc
from ..model.device import Device, Devices, get_device_fuzzy, get_devices_from_file, \
  load_device_with_name
from ..model.video import Video
from ..parse import DEVICE_INFO


def show_devices(devices: Devices):
  for device in devices:
    print(f'  - [b]{device.name}')


def _get_command(
  name: str,
  path: Path,
  threads: int,
) -> bool:
  video = Video.from_path(path)

  if not (device := _get_device_from_name(name)):
    raise Exit(code=Rc.no_matching_device)

  if not should_transcode(device, video):
    return False

  formats = device.transcode_to(video)
  stream, _ = get_stream(video, formats, threads)

  cmd = get_ffmpeg_cmd(stream)
  print(f'[b]{cmd}')

  return True


def _inspect(
  name: str,
  path: Path,
) -> bool:
  video = Video.from_path(path)

  if not (device := _get_device_from_name(name)):
    raise Exit(code=Rc.no_matching_device)

  if not should_transcode(device, video):
    return False

  name = device.name

  print(f'🔄️ [b green]Need to convert [b blue]"{video.path}"[/] to play on [yellow]{name}[/]...[/]')
  print('[b green]Must convert from:')
  print(checklist(video.formats.text))

  print('[b green]To:')
  formats = device.transcode_to(video)
  print(checklist(formats.text))

  return True


def _get_device_from_name(
  name: str,
  device_file: Path = DEVICE_INFO,
) -> Device | None:
  devices = get_devices_from_file(device_file)

  if not (dev := get_device_fuzzy(name, devices)):
    print(f'[b red]Device name [yellow]"{name}"[/] not found[/], please use one of these:')
    show_devices(devices)

    return None

  return dev


def _convert(
  name: str,
  path: Path,
  threads: int,
):
  video = Video.from_path(path)
  device = load_device_with_name(name)

  if not should_transcode(device, video):
    return

  formats = device.transcode_to(video)
  transcode_video(video, formats, threads)


def indent(text: str | Any) -> str:
  if not isinstance(text, str):
    text: str = str(text)

  lines = text.split('\n')

  return '\n'.join(f'\t{line}' for line in lines)


def checklist(text: str | Any) -> str:
  if not isinstance(text, str):
    text: str = str(text)

  lines = text.split('\n')

  return '\n'.join(f'  - {line}' for line in lines)


def check_paths(paths: list[Path]) -> NoReturn | None:
  if not paths:
    print('[b red]No paths supplied.')
    raise Exit(code=Rc.missing_args)

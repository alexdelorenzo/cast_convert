from __future__ import annotations

from pathlib import Path
from typing import NoReturn

from click.exceptions import Exit
from rich.markup import escape
from rich import print

from ..core.convert.run import get_ffmpeg_cmd, get_stream
from ..core.convert.transcode import should_transcode
from ..core.base import Peekable, Rc, checklist, esc, tab, tab_list
from ..core.model.device import Device, Devices, get_device_fuzzy, get_devices_from_file
from ..core.model.video import Video
from ..core.parse import DEVICE_INFO


def show_devices(devices: Devices, details: bool = False):
  for device in (devices := Peekable(devices)):
    tab_list(f'[b]{device.name}', out=True)

    if details:
      for profile in device.video_profiles:
        tab_list(profile.codec.name, tabs=2, out=True)
        tab_list(profile.text, tabs=3, out=True)

      if not devices.is_empty:
        print()


def _get_command(
  name: str,
  path: Path,
  threads: int,
) -> bool:
  video = Video.from_path(path)

  if not (device := _get_device_from_name(name)):
    raise Exit(Rc.no_matching_device)

  if not should_transcode(device, video):
    return False

  formats = device.transcode_to(video)
  stream, _ = get_stream(video, formats, threads)

  cmd = get_ffmpeg_cmd(stream, video.path)
  print(f'[b]{escape(cmd)}')

  return True


def _inspect(
  name: str,
  path: Path,
) -> bool:
  video = Video.from_path(path)

  if not (device := _get_device_from_name(name)):
    raise Exit(Rc.no_matching_device)

  if not should_transcode(device, video):
    return False

  name = device.name

  print(f'[b red][🔄️] Need to convert [b blue]"{esc(video.path)}"[/] to play on [yellow]{name}[/]...[/]')
  print(tab('[b red]Must convert from:'))
  tab_list(video.formats.text, out=True)

  print(tab('[b green]To:'))
  formats = device.transcode_to(video)
  tab_list(formats.text, out=True)

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


def check_paths(paths: list[Path]) -> NoReturn | None:
  if not paths:
    print('[b red][❌] No paths supplied.')
    raise Exit(Rc.missing_args)

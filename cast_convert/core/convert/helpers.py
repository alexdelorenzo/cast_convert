from __future__ import annotations
from pathlib import Path

from rich import print

from .transcode import should_transcode
from ..base import first
from ..model.device import Device, get_devices_from_file
from ..model.video import Video
from .run import get_ffmpeg_cmd, get_stream
from ..parse import DEVICE_INFO


def show_devices(devices: tuple[Device]):
  for device in devices:
    print(f'\t - [b]{device.name}')


def _get_command(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  device = get_device_with_name(name)

  if not should_transcode(device, video):
    return

  formats = device.transcode_to(video)
  _, stream = get_stream(video, formats)

  cmd = get_ffmpeg_cmd(stream)
  print(f'[b]{cmd}')


def _inspect(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  device = get_device_with_name(name)

  if not should_transcode(device, video):
    return

  print(f'These attributes will be converted from  {video.path}:\n\t', end='')
  formats = device.transcode_to(video)
  print(formats)


def get_device_with_name(
  name: str,
  device_file: Path = DEVICE_INFO,
) -> Device | None:
  name = name.casefold()
  devices = get_devices_from_file(device_file)

  if not (dev := first(d for d in devices if d.name.casefold() == name)):
    print(f'[b red]Device name "{name}" not found[/], please use one of these:')
    show_devices(devices)
    return None

  return dev

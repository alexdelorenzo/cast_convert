from __future__ import annotations
from pathlib import Path
from typing import Final, cast

from rich import print

from ..core.base import first
from ..core.convert.run import get_ffmpeg_cmd, get_stream, transcode_video
from ..core.model.device import Device
from ..core.model.video import Video
from ..core.parse import DEVICE_INFO


DEFAULT_MODEL: Final[str] = 'Chromecast 1st Gen'


Devices = tuple[Device]


def get_devices(
  device_file: Path = DEVICE_INFO,
) -> Devices:
  devices = tuple(Device.from_yaml(device_file))
  return cast(Devices, devices)


def get_device(
  name: str,
  device_file: Path = DEVICE_INFO,
) -> Device | None:
  name = name.casefold()
  devices = get_devices(device_file)

  if not (dev := first(d for d in devices if d.name.casefold() == name)):
    print(f'[b red]Device name "{name}" not found[/b red], please use one of these:')
    show_devices(devices)
    return None

  return dev


def show_devices(devices: tuple[Device]):
  for device in devices:
    print(f'\t - [b]{device.name}')


def should_transcode(
  device: Device,
  video: Video,
) -> bool:
  if not device:
    return False

  if device.can_play(video):
    print(f'No need to transcode {video.name} for {device.name}.')
    return False

  return True


def _get_command(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  device = get_device(name)

  if not should_transcode(device, video):
    return

  formats = device.transcode_to(video)
  _, stream = get_stream(video, formats)

  cmd = get_ffmpeg_cmd(stream)
  print(f'[b]{cmd}')


def _convert(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  device = get_device(name)

  if not should_transcode(device, video):
    return

  formats = device.transcode_to(video)
  transcode_video(video, formats)


def _inspect(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  device = get_device(name)

  if not should_transcode(device, video):
    return

  print(f'These attributes will be converted from  {video.path}:\n\t', end='')
  formats = device.transcode_to(video)
  print(formats)

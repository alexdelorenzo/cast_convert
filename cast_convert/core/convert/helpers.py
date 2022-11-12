from __future__ import annotations
from pathlib import Path

from rich import print

from ..base import first
from ..model.device import Device, get_device_with_name, load_device_with_name, get_devices_from_file
from ..model.video import Video
from ..parse import DEVICE_INFO
from .run import get_ffmpeg_cmd, get_stream, transcode_video
from .transcode import should_transcode


def show_devices(devices: tuple[Device]):
  for device in devices:
    print(f'\t - [b]{device.name}')


def _get_command(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  device = _get_device_from_name(name)

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
  device = _get_device_from_name(name)

  if not should_transcode(device, video):
    return

  print(f'These attributes will be converted from {video.path}:')
  formats = device.transcode_to(video)
  print(formats)


def _get_device_from_name(
  name: str,
  device_file: Path = DEVICE_INFO,
) -> Device | None:
  devices = get_devices_from_file(device_file)

  if not (dev := get_device_with_name(name, devices)):
    print(f'[b red]Device name "{name}" not found[/], please use one of these:')
    show_devices(devices)

    return None

  return dev


def _convert(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  device = load_device_with_name(name)

  if not should_transcode(device, video):
    return

  formats = device.transcode_to(video)
  transcode_video(video, formats)

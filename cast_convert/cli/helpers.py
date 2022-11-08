from __future__ import annotations

from pathlib import Path

from cast_convert.core.base import first
from cast_convert.core.convert.run import get_ffmpeg_cmd, get_stream
from cast_convert.core.model.device import Device
from cast_convert.core.model.video import Video


def _get_command(
  name: str,
  path: Path,
):
  video = Video.from_path(path)
  devices: tuple[Device] = tuple(Device.from_yaml())  # type: ignore
  device: Device

  if not (device := first(dev for dev in devices if dev.name == name)):
    print(f'Device name "{name}" not found, please use one of these: ')

    for device in devices:
      print(f'\t - {device.name}')

    return

  if device.can_play(video):
    print(f'No need to transcode {video.name} for {device.name}.')
    return

  formats = device.transcode_to(video)
  _, stream = get_stream(video, formats)

  cmd = get_ffmpeg_cmd(stream)
  print(cmd)

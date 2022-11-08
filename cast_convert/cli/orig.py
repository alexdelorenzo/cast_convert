from __future__ import annotations

from pathlib import Path
from typing import Final

import typer

from cast_convert.core.base import first
from ..core.convert.run import get_ffmpeg_cmd, get_stream, transcode_video as transcode_video_via_formats
from ..core.convert.transcode import transcode_video
from ..core.model.video import Video
from ..core.model.device import Device


app: Final[typer.Typer] = typer.Typer()


@app.command()
def get_command(
  path: Path,
  name: str,
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
  _, stream = get_stream(video, formats, formats.container)

  cmd = get_ffmpeg_cmd(stream)
  print(cmd)

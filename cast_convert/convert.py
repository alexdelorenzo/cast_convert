from __future__ import annotations
from enum import StrEnum, auto
from pathlib import Path
from typing import Final

from .base import VideoProfile, VideoCodec, AudioProfile, AudioCodec, Container, Formats, \
  Extension, first
from .exceptions import UnknownFormat
from .parse import ENCODERS
from .video import Video, VideoMetadata
from .device import Device

import ffmpeg


DEFAULT_EXT: Final[Extension] = Container.matroska.to_extension()  # type: ignore
SUFFIX: Final[str] = '_transcoded'


class FfmpegArg(StrEnum):
  acodec: str = auto()
  vcodec: str = auto()
  scodec: str = auto()
  copy: str = auto()


Arg = FfmpegArg | str
Args = dict[Arg, Arg]


DEFAULT_ARGS: Final[Args] = {
  FfmpegArg.acodec: FfmpegArg.copy,
  FfmpegArg.vcodec: FfmpegArg.copy,
  FfmpegArg.scodec: FfmpegArg.copy,
}


def transcode_video(video: Video, formats: Formats) -> Video:
  container, video_profile, audio_profile = formats
  video_codec, resolution, fps, level = video_profile
  [audio_codec] = formats.audio_profile

  args: Args = DEFAULT_ARGS.copy()

  if audio_codec:
    encoders = ENCODERS[audio_codec]
    args[FfmpegArg.acodec] = first(encoders)

  if video_codec:
    encoders = ENCODERS[video_codec]
    args[FfmpegArg.vcodec] = first(encoders)

  if fps:
    pass

  else:
    pass

  if resolution:
    pass

  else:
    pass

  if level:
    pass

  else:
    pass

  new_ext: str = video.path.suffix

  if container:
    try:
      new_ext = container.to_extension()

    except UnknownFormat as e:
      new_ext = DEFAULT_EXT

  new_path: Path = (
    video.path
    .with_stem(f'{video.path.stem}{SUFFIX}')
    .with_suffix(new_ext)
  )

  stream = (
    ffmpeg
    .input(video.path)
    .output(new_path, **args)
  )
  stream.run()

  return Video.from_path(new_path)

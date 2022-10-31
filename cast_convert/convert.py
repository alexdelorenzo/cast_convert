from __future__ import annotations
from enum import StrEnum, auto
from pathlib import Path
from typing import Final

from .base import VideoProfile, VideoCodec, AudioProfile, AudioCodec, \
  Container, Formats, Extension, first
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
  # TODO: Finish this stub
  container, video_profile, audio_profile, subtitle = formats
  new_path = get_new_path(video, container)

  args = get_args(formats)

  stream = (
    ffmpeg
    .input(video.path)
    .output(new_path, **args)
  )
  stream.run()

  return Video.from_path(new_path)


def get_new_path(video: Video, container: Container) -> Path:
  ext: Extension = video.path.suffix

  if container and not (ext := container.to_extension()):
    ext = DEFAULT_EXT

  new_path: Path = (
    video.path
    .with_stem(f'{video.path.stem}{SUFFIX}')
    .with_suffix(ext)
  )

  return new_path


def get_args(formats: Formats) -> Args:
  video_codec, resolution, fps, level = formats.video_profile
  [audio_codec] = formats.audio_profile
  subtitle = formats.subtitle  # TODO: Finish this stub

  args: Args = DEFAULT_ARGS.copy()

  if audio_codec:
    encoders = ENCODERS[audio_codec]
    args[FfmpegArg.acodec] = first(encoders)

  if video_codec:
    encoders = ENCODERS[video_codec]
    args[FfmpegArg.vcodec] = first(encoders)

  if fps:
    pass

  if resolution:
    pass

  if level:
    pass

  return args

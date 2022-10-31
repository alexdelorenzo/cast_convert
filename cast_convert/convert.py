from __future__ import annotations

import logging
from enum import StrEnum, auto
from pathlib import Path
from typing import Final

from .base import VideoProfile, VideoCodec, AudioProfile, AudioCodec, \
  Container, Formats, Extension, first, VideoFormat
from .exceptions import UnknownFormat
from .parse import ENCODERS
from .video import Video
from .device import Device

import ffmpeg


DOT: Final[str] = '.'

DEFAULT_EXT: Final[Extension] = Container.matroska.to_extension()  # type: ignore
TRANSCODE_SUFFIX: Final[str] = '_transcoded'
HWACCEL_DEVICE: Final[Path] = Path('/dev/dri/renderD128')


class FfmpegArg(StrEnum):
  acodec: str = auto()
  vcodec: str = auto()
  scodec: str = auto()
  fps: str = auto()
  r: str = auto()

  hwaccel: str = auto()
  hwaccel_output_format: str = auto()
  vaapi_device: str = auto()

  copy: str = auto()
  vaapi: str = auto()

  scale: str = auto()


Arg = FfmpegArg | str
Args = dict[Arg, Arg]


DEFAULT_OUTPUT_ARGS: Final[Args] = {
  FfmpegArg.acodec: FfmpegArg.copy,
  FfmpegArg.vcodec: FfmpegArg.copy,
  FfmpegArg.scodec: FfmpegArg.copy,
}

HWACCEL_ARGS: Final[Args] = {
  FfmpegArg.hwaccel: FfmpegArg.vaapi,
  FfmpegArg.hwaccel_output_format: FfmpegArg.vaapi,
  FfmpegArg.vaapi_device: str(HWACCEL_DEVICE),
}

DEFAULT_INPUT_ARGS: Final[Args] = {}


def transcode_video(video: Video, formats: Formats) -> Video:
  # TODO: Finish this stub
  container, video_profile, audio_profile, subtitle = formats

  input_args = get_input_args(formats)
  output_args = get_output_args(formats)

  new_path = get_new_path(video, container)

  stream = ffmpeg.input(
    str(video.path),
    **input_args
  )

  if filters := get_filters(stream, formats):
    stream = filters

  stream = stream.output(
    str(new_path),
    **output_args
  )

  cmd: str = ' '.join(stream.compile())
  logging.info(f'Running command: {cmd}')

  stream.run()

  return Video.from_path(new_path)


def get_new_path(
  video: Video,
  container: Container,
  suffix: str = TRANSCODE_SUFFIX
) -> Path:
  ext: Extension = video.path.suffix

  if container and not (ext := container.to_extension()):
    ext = DEFAULT_EXT

  if not ext.startswith(DOT):
    ext = DOT + ext

  new_path: Path = (
    video.path
    .with_stem(f'{video.path.stem}{suffix}')
    .with_suffix(ext)
  )

  return new_path


def get_output_args(formats: Formats) -> Args:
  # TODO: Finish this stub
  args: Args = DEFAULT_OUTPUT_ARGS.copy()

  if (profile := formats.audio_profile) and (codec := profile.codec):
    encoders = ENCODERS[codec]
    args[FfmpegArg.acodec] = first(encoders)

  if (profile := formats.video_profile) and (codec := profile.codec):
    encoders = ENCODERS[codec]
    args[FfmpegArg.vcodec] = first(encoders)

  if subtitle := formats.subtitle:
    pass

  if not profile:
    return args

  video_codec, resolution, fps, level = profile

  if fps:
    args[FfmpegArg.r] = str(fps)

  if resolution:
    pass

  if level:
    pass

  return args


def get_input_args(formats: Formats) -> Args:
  video_codec, resolution, fps, level = formats.video_profile
  args: Args = DEFAULT_INPUT_ARGS.copy()

  if resolution:
    pass

  if level:
    pass

  return args


def get_filters(stream: ffmpeg.Stream, formats: Formats) -> ffmpeg.Stream | None:
  video_codec, resolution, fps, level = formats.video_profile
  stream: ffmpeg.Stream | None = None

  if resolution:
    stream = ffmpeg.filter(
      stream,
      FfmpegArg.scale,
      f'{resolution}:-1'
    )

  return stream

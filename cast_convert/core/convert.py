from __future__ import annotations

from enum import StrEnum, auto
from pathlib import Path
from typing import Final
import logging

import ffmpeg

from .base import first, Resolution
from .models.formats import (
  Codecs, Formats,
)
from .models.codecs import AudioCodec, Container, Subtitle, VideoCodec
from .parse import (
  Alias, Aliases, AUDIO_ENCODERS, SUBTITLE_ENCODERS,
  VIDEO_ENCODERS, Extension,
)
from .video import Video


DOT: Final[str] = '.'
SCALE_RESOLUTION: Final[Resolution] = -1

DEFAULT_EXT: Final[Extension] = Container.matroska.to_extension()  # type: ignore
TRANSCODE_SUFFIX: Final[str] = '_transcoded'
HWACCEL_DEVICE: Final[Path] = Path('/dev/dri/renderD128')


class FfmpegArg(StrEnum):
  acodec: str = auto()
  vcodec: str = auto()
  scodec: str = auto()
  vprofile: str = auto()
  vlevel: str = auto()
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


def get_encoder(codec: Codecs) -> Alias:
  encoders: Aliases

  match codec:
    case AudioCodec():
      encoders = AUDIO_ENCODERS[codec]

    case VideoCodec():
      encoders = VIDEO_ENCODERS[codec]

    case Subtitle():
      encoders = SUBTITLE_ENCODERS[codec]

    case obj:
      raise TypeError(f"{obj} not a codec")

  return first(encoders)


def transcode_video(video: Video, formats: Formats) -> Video:
  container, video_profile, audio_profile, subtitle = formats

  input_args = get_input_args(formats)
  output_args = get_output_args(video, formats)
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
  suffix: str = TRANSCODE_SUFFIX,
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


def get_output_args(video: Video, formats: Formats) -> Args:
  args: Args = DEFAULT_OUTPUT_ARGS.copy()

  if (profile := formats.audio_profile) and (codec := profile.codec):
    args[FfmpegArg.acodec] = get_encoder(codec)

  if (profile := formats.video_profile) and (codec := profile.codec):
    args[FfmpegArg.vcodec] = get_encoder(codec)

  if codec := formats.subtitle:
    args[FfmpegArg.scodec] = get_encoder(codec)

  if not profile:
    return args

  *_, fps, level = profile

  if fps:
    args[FfmpegArg.r] = str(fps)

  if level:
    args[FfmpegArg.vlevel] = str(level)

    if FfmpegArg.vcodec not in args:
      codec = video.formats.video_profile.codec
      args[FfmpegArg.vcodec] = get_encoder(codec)

  return args


def get_input_args(formats: Formats) -> Args:
  video_codec, resolution, fps, level = formats.video_profile
  args: Args = DEFAULT_INPUT_ARGS.copy()

  return args


def get_filters(stream: ffmpeg.Stream, formats: Formats) -> ffmpeg.Stream | None:
  video_codec, resolution, fps, level = formats.video_profile
  filters: ffmpeg.Stream | None = None

  if resolution:
    filters = ffmpeg.filter(
      stream,
      FfmpegArg.scale,
      resolution,
      SCALE_RESOLUTION,
    )

  return filters

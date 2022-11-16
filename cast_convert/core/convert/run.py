from __future__ import annotations

from enum import StrEnum, auto
from pathlib import Path
from typing import Final
import logging

import ffmpeg
from ffmpeg.nodes import FilterableStream, OutputStream

from ..media.formats import Formats
from ..media.codecs import AudioCodec, Codecs, Container, Subtitle, VideoCodec
from ..base import first, Resolution
from ..parse import Alias, Aliases, AUDIO_ENCODERS, SUBTITLE_ENCODERS, VIDEO_ENCODERS, Extension
from ..model.video import Video


DOT: Final[str] = '.'
SCALE_RESOLUTION: Final[Resolution] = -2  # see: https://stackoverflow.com/a/29582287

DEFAULT_EXT: Final[Extension] = Container.matroska.to_extension()  # type: ignore
TRANSCODE_SUFFIX: Final[str] = '_transcoded'
HWACCEL_DEVICE: Final[Path] = Path('/dev/dri/renderD128')


class FfmpegOpt(StrEnum):
  acodec: str = auto()
  vcodec: str = auto()
  scodec: str = auto()
  vprofile: str = auto()
  vlevel: str = auto()
  fps: str = auto()
  r: str = auto()

  fflags: str = auto()
  movflags: str = auto()

  hwaccel: str = auto()
  hwaccel_output_format: str = auto()
  vaapi_device: str = auto()

  scale: str = auto()
  threads: str = auto()


class FfmpegArg(StrEnum):
  y: str = '-y'


class FfmpegVal(StrEnum):
  copy: str = auto()
  vaapi: str = auto()
  faststart: str = auto()

  genpts: str = '+genpts'
  scale_resolution: str = str(SCALE_RESOLUTION)


Option = FfmpegOpt | str
Arg = FfmpegArg | str
Val = FfmpegVal | str | float | int

Args = list[Arg]
Options = dict[Option, Val]


DEFAULT_OUTPUT_OPTS: Final[Options] = {
  FfmpegOpt.acodec: FfmpegVal.copy,
  FfmpegOpt.vcodec: FfmpegVal.copy,
  FfmpegOpt.scodec: FfmpegVal.copy,
  FfmpegOpt.movflags: FfmpegVal.faststart,
}

HWACCEL_OPTS: Final[Options] = {
  FfmpegOpt.hwaccel: FfmpegVal.vaapi,
  FfmpegOpt.hwaccel_output_format: FfmpegVal.vaapi,
  FfmpegOpt.vaapi_device: str(HWACCEL_DEVICE),
}

DEFAULT_INPUT_OPTS: Final[Options] = {
  FfmpegOpt.fflags: FfmpegVal.genpts,
}

GLOBAL_ARGS: Final[Args] = [
  FfmpegArg.y,
]

GLOBAL_OPTS: Final[Options] = {}


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


def transcode_video(video: Video, formats: Formats, threads: int) -> Video:
  stream, path = get_stream(video, formats, threads)
  cmd = get_ffmpeg_cmd(stream)

  logging.info(f'Running command: {cmd}')
  stream.run()  # type: ignore

  return Video.from_path(path)


def get_ffmpeg_cmd(stream: OutputStream) -> str:
  args = stream.compile()  # type: ignore
  return ' '.join(args)


def get_stream(
  video: Video,
  formats: Formats,
  threads: int,
) -> tuple[OutputStream, Path]:
  input_opts = get_input_opts(formats)
  output_opts = get_output_opts(video, formats, threads)
  new_path = get_new_path(video, formats)

  stream = ffmpeg.input(
    str(video.path),
    **input_opts,
  )

  if filters := get_video_filters(stream, formats):
    output_opts.pop(FfmpegOpt.vcodec)
    stream = filters

  stream = stream.output(
    str(new_path),
    **output_opts,
  )

  stream = stream.global_args(
    *GLOBAL_ARGS,
    **GLOBAL_OPTS,
  )

  return stream, new_path


def get_new_path(
  video: Video,
  formats: Formats,
  suffix: str = TRANSCODE_SUFFIX,
) -> Path:
  container, video_profile, audio, subtitle = formats
  codec, *_ = video_profile

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


def get_output_opts(video: Video, formats: Formats, threads: int) -> Options:
  opts: Options = DEFAULT_OUTPUT_OPTS.copy()

  if (profile := formats.audio_profile) and (codec := profile.codec):
    opts[FfmpegOpt.acodec] = get_encoder(codec)

  if (profile := formats.video_profile) and (codec := profile.codec):
    opts[FfmpegOpt.vcodec] = get_encoder(codec)

  if codec := formats.subtitle:
    opts[FfmpegOpt.scodec] = get_encoder(codec)

  if not profile:
    return opts

  *_, fps, level = profile

  if fps:
    opts[FfmpegOpt.r] = fps

  if level:
    opts[FfmpegOpt.vlevel] = level

    if FfmpegOpt.vcodec not in opts:
      codec = video.formats.video_profile.codec
      opts[FfmpegOpt.vcodec] = get_encoder(codec)

  opts[FfmpegOpt.threads] = threads

  return opts


def get_input_opts(formats: Formats) -> Options:
  opts: Options = DEFAULT_INPUT_OPTS.copy()

  if not formats.video_profile:
    return opts

  video_codec, resolution, fps, level = formats.video_profile

  return opts


def get_video_filters(
  stream: FilterableStream,
  formats: Formats,
) -> FilterableStream | None:
  if not formats.video_profile:
    return None

  video_codec, resolution, fps, level = formats.video_profile
  filters: FilterableStream | None = None

  if resolution:
    filters = ffmpeg.filter(
      stream,
      FfmpegOpt.scale,
      resolution,
      FfmpegVal.scale_resolution,
    )

  return filters

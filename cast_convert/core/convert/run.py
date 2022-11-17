from __future__ import annotations

from enum import StrEnum, auto
from pathlib import Path
from shlex import quote
from typing import Final, Iterable
import logging

import ffmpeg
from ffmpeg.nodes import FilterableStream, OutputStream

from .transcode import should_transcode
from ..media.formats import Formats
from ..media.codecs import AudioCodec, Codecs, Container, Subtitle, VideoCodec
from ..base import DEFAULT_REPLACE, DEFAULT_THREADS, JOIN_COMMAND, first, Resolution
from ..model.device import load_device_with_name
from ..parse import Alias, Aliases, AUDIO_ENCODERS, SUBTITLE_ENCODERS, VIDEO_ENCODERS, Extension
from ..model.video import Video


DOT: Final[str] = '.'

DEFAULT_EXT: Final[Extension] = Container.matroska.to_extension()
TRANSCODE_SUFFIX: Final[str] = '_transcoded'

SCALE_RESOLUTION: Final[Resolution] = -2  # see: https://stackoverflow.com/a/29582287
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
  vaapi_device: str = str(HWACCEL_DEVICE)


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
  FfmpegOpt.vaapi_device: FfmpegVal.vaapi_device,
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


def transcode_video(
  video: Video,
  formats: Formats,
  replace: bool = DEFAULT_REPLACE,
  threads: int = DEFAULT_THREADS,
) -> Video:
  stream, path = get_stream(video, formats, threads)
  cmd = get_ffmpeg_cmd(stream, video.path)

  logging.info(f'Running command: {cmd}')
  stream.run()  # type: ignore

  if replace and path:
    path.rename(video.path)

  return Video.from_path(path)


def get_ffmpeg_cmd(
  stream: OutputStream,
  path: Path,
) -> str:
  parent: Path = path.parent

  args: Iterable[str] = (
    quote(arg) if Path(arg).parent == parent else arg
    for arg in stream.compile()  # type: ignore
  )

  return JOIN_COMMAND.join(args)


def get_stream(
  video: Video,
  formats: Formats,
  threads: int = DEFAULT_THREADS,
) -> tuple[OutputStream, Path]:
  input_opts = get_input_opts(formats)
  output_opts = get_output_opts(video, formats, threads)
  new_path = get_new_path(video, formats)

  stream = ffmpeg.input(
    str(video.path),
    **input_opts,
  )

  if filters := get_video_filters(stream, formats):
    if output_opts.get(FfmpegOpt.vcodec) is FfmpegVal.copy:
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


def get_output_opts(
  video: Video,
  formats: Formats,
  threads: int = DEFAULT_THREADS,
) -> Options:
  opts: Options = DEFAULT_OUTPUT_OPTS.copy()
  opts[FfmpegOpt.threads] = threads

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


def convert_from_name_path(
  name: str,
  path: Path,
  replace: bool = DEFAULT_REPLACE,
  threads: int = DEFAULT_THREADS,
) -> bool:
  video = Video.from_path(path)
  device = load_device_with_name(name)

  if not should_transcode(device, video):
    return False

  formats = device.transcode_to(video)

  try:
    transcode_video(video, formats, replace, threads)

  except Exception as e:
    logging.exception(e)
    logging.error(f'Error while converting {video} to {formats}')
    return False

  return True

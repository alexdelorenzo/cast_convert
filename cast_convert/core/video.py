from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Iterable

from pymediainfo import MediaInfo

from .base import (
  VideoProfile, AudioProfile, Container,
  AudioCodec, VideoCodec, normalize_info, DEFAULT_VIDEO_FPS,
  DEFAULT_VIDEO_LEVEL, Formats, Level, Fps, Subtitle,
  VideoFormat, get_name, LEVEL_SEP, AT,
)
from .parse import Yaml


@dataclass
class Video:
  name: str
  path: Path

  formats: Formats
  data: MediaInfo

  @classmethod
  def from_path(cls, path: Path) -> Self:
    data: MediaInfo = MediaInfo.parse(path)

    [general] = data.general_tracks
    title = general.file_name or general.complete_name

    container = Container.from_info(general.format)
    subtitle = Subtitle.from_info(general.text_codecs)

    video_profile = get_video_profile(data)
    audio_profile = get_audio_profile(data)

    formats = Formats(
      container=container,
      video_profile=video_profile,
      audio_profile=audio_profile,
      subtitle=subtitle,
    )

    return cls(
      name=title,
      path=path.absolute(),
      formats=formats,
      data=data,
    )

  def is_compatible(self, other: VideoFormat) -> bool:
    return is_compatible(self, other)


def get_audio_profile(data: MediaInfo) -> AudioProfile | None:
  if not data.audio_tracks:
    return None

  audio, *_ = data.audio_tracks

  name: str = audio.codec_id_hint or audio.format
  codec = AudioCodec.from_info(name)

  return AudioProfile(codec)


def get_video_profile(data: MediaInfo) -> VideoProfile | None:
  if not data.video_tracks:
    return None

  [video] = data.video_tracks
  fmts = video.format, video.codec_id, video.codec_id_hint
  codec: VideoCodec = VideoCodec.unknown  # type: ignore

  for fmt in fmts:
    if (codec := VideoCodec.from_info(fmt)) is not VideoCodec.unknown:
      break

  height, width = video.height, video.width
  fps = video.original_frame_rate or video.frame_rate
  profile = video.format_profile

  return VideoProfile(
    codec=codec,
    resolution=int(height),
    fps=Fps(fps if fps else DEFAULT_VIDEO_FPS),
    level=profile_to_level(profile)
  )


def is_compatible(video: Video, fmt: VideoFormat) -> bool:
  container, video_profile, audio_profile, subtitle = video.formats

  match fmt:
    case VideoProfile(codec, resolution, fps, level):
      _codec, _resolution, _fps, _level = video_profile

      return (
        _codec is codec and
        _resolution <= resolution and
        _fps <= fps and
        _level <= level
      )

    case AudioProfile(codec):
      return audio_profile.codec is codec

    case VideoCodec() as codec:
      return video_profile.codec is codec

    case AudioCodec() as codec:
      return audio_profile.codec is codec

    case Container() as _container:
      return container is _container

    case Subtitle() as _subtitle:
      if not _subtitle:
        return True

      return subtitle is _subtitle

  raise TypeError(f'Cannot compare with {get_name(fmt)}')


def profile_to_level(profile: str | None) -> Level:
  if not (level := profile):
    return DEFAULT_VIDEO_LEVEL

  match level.split(AT):
    case (name, level) | (name, level, _) if LEVEL_SEP in level:
      level = level.strip(LEVEL_SEP)

    case (name, level) | (name, level, _):
      level = level

  if not (level := normalize_info(level, str.isnumeric)):
    return DEFAULT_VIDEO_LEVEL

  match [*level]:
    case [val]:
      return Level(f'{val}.0')

    case big, *small:
      small = ''.join(small)
      return Level(f'{big}.{small}')

  return DEFAULT_VIDEO_LEVEL


def get_video_profiles(profiles: Yaml) -> Iterable[VideoProfile]:
  profile: Yaml
  attrs: Yaml

  for profile in profiles:
    [name, attrs], *_ = profile.items()
    codec = VideoCodec.from_info(name)

    yield VideoProfile(
      codec=codec,
      resolution=int(attrs.get('resolution')),
      fps=Fps(attrs.get('fps')),
      level=Level(attrs.get('level')),
    )
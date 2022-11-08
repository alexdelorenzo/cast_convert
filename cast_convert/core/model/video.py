from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Iterable, cast

from pymediainfo import MediaInfo

from ..base import (
  IsCompatible, normalize_info, DEFAULT_VIDEO_FPS, DEFAULT_VIDEO_LEVEL,
  Level, Fps, LEVEL_SEP, AT, Resolution,
)
from ..media.profiles import AudioProfile, VideoProfile
from ..media.base import get_name
from ..media.formats import Formats, VideoFormat, is_compatible
from ..media.codecs import AudioCodec, Container, Subtitle, VideoCodec
from ..parse import Yaml


@dataclass
class Video(IsCompatible):
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
    return is_compatible(self.formats, other)


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
  codec: VideoCodec = cast(VideoCodec.unknown, VideoCodec)

  for fmt in fmts:
    if (codec := VideoCodec.from_info(fmt)) is not VideoCodec.unknown:
      break

  height, width = video.height, video.width
  fps = video.original_frame_rate or video.frame_rate
  profile = video.format_profile

  return VideoProfile(
    codec=codec,
    resolution=Resolution(height),
    fps=Fps(fps if fps else DEFAULT_VIDEO_FPS),
    level=profile_to_level(profile)
  )


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
      resolution=Resolution(attrs.get('resolution')),
      fps=Fps(attrs.get('fps')),
      level=Level(attrs.get('level')),
    )

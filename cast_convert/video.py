from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Self, Iterable

from pymediainfo import MediaInfo

from .base import VideoProfile, AudioProfile, Container, \
  AudioCodec, VideoCodec, normalize_info, DEFAULT_FPS, \
  DEFAULT_LEVEL, PROFILE_SEP, Formats
from .parse import Yaml


Codecs = AudioCodec | VideoCodec
Profiles = AudioProfile | VideoProfile
VideoMetadata = Codecs | Profiles


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
    video_profile = get_video_profile(data)
    audio_profile = get_audio_profile(data)

    formats = Formats(
      container=container,
      video_profile=video_profile,
      audio_profile=audio_profile,
    )

    return cls(
      name=title,
      path=path.absolute(),
      formats=formats,
      data=data,
    )

  def is_compatible(self, other: VideoMetadata) -> bool:
    return is_compatible(self, other)


def get_audio_profile(data: MediaInfo) -> AudioProfile | None:
  if not data.audio_tracks:
    return None

  audio, *_ = data.audio_tracks

  audio_name: str = audio.codec_id_hint or audio.format
  audio_codec = AudioCodec.from_info(audio_name)

  return  AudioProfile(audio_codec)


def get_video_profile(data: MediaInfo) -> VideoProfile | None:
  if not data.video_tracks:
    return None

  [video] = data.video_tracks

  if (codec := VideoCodec.from_info(video.format)) == VideoCodec.unknown:
    codec = VideoCodec.from_info(video.codec_id or video.codec_id_hint)

  height, width = video.height, video.width
  fps = video.original_frame_rate
  profile = video.format_profile

  return VideoProfile(
    codec=codec,
    resolution=int(height),
    fps=float(fps if fps else DEFAULT_FPS),
    level=profile_to_level(profile)
  )


def is_compatible(video: Video, other: VideoMetadata) -> bool:
  container, video_profile, audio_profile = video.formats

  match other:
    case VideoProfile(codec, resolution, fps, level):
      _codec, _resolution, _fps, _level = video_profile

      return (
        _codec == codec and
        _resolution <= resolution and
        _fps <= fps and
        _level <= level
      )

    case AudioProfile(codec):
      return audio_profile.codec == codec

    case VideoCodec() as codec:
      return video_profile.codec == codec

    case AudioCodec() as codec:
      return audio_profile.codec == codec

  raise TypeError(type(other))


def profile_to_level(profile: str | None) -> float:
  if not (level := profile):
    return DEFAULT_LEVEL

  if PROFILE_SEP in level:
    name, level = level.split(PROFILE_SEP)

  level = normalize_info(level)

  if not level.isnumeric():
    return DEFAULT_LEVEL

  match [*level]:
    case [val]:
      return float(val)

    case [big, small]:
      return float(f'{big}.{small}')

  return DEFAULT_LEVEL


def get_video_profiles(info: Yaml) -> Iterable[VideoProfile]:
  codec_info: Yaml

  for codec_info in info:
    [name, attrs], *_ = codec_info.items()
    codec = VideoCodec.from_info(name)

    yield VideoProfile(
      codec=codec,
      resolution=attrs.get('resolution'),
      fps=float(attrs.get('fps')),
      level=float(attrs.get('level')),
    )

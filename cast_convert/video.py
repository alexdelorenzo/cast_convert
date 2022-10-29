from dataclasses import dataclass
from pathlib import Path
from typing import Final, Self

from pymediainfo import MediaInfo

from .base import VideoProfile, AudioProfile, Container, AudioCodec, VideoCodec


PROFILE_SEP: Final[str] = '@L'
DEFAULT_FPS: Final[float] = 0.0
DEFAULT_LEVEL: Final[float] = 0.0


VideoMetadata = AudioProfile | VideoProfile | AudioCodec | VideoCodec


@dataclass
class Video:
  name: str
  path: Path

  container: Container
  video_profile: VideoProfile
  audio_profile: AudioProfile

  data: MediaInfo

  @classmethod
  def from_path(cls, path: Path) -> Self:
    data: MediaInfo = MediaInfo.parse(path)

    [gen] = data.general_tracks
    [video] = data.video_tracks
    audio, *_ = data.audio_tracks

    title = gen.complete_name
    container = Container.from_info(gen.format)
    codec = VideoCodec.from_info(video.format)
    height, width = video.height, video.width
    audio_codec = AudioCodec.from_info(audio.codec_id_hint)
    fps = video.original_frame_rate
    profile = video.format_profile

    video_profile = VideoProfile(
      codec=codec,
      resolution=int(width),
      fps=float(fps if fps else DEFAULT_FPS),
      level=profile_to_level(profile)
    )

    audio_profile = AudioProfile(audio_codec)

    return cls(
      name=title,
      path=path.absolute(),
      container=container,
      data=data,
      video_profile=video_profile,
      audio_profile=audio_profile,
    )

  def is_compatible(self, other: VideoMetadata) -> bool:
    return is_compatible(self, other)


def is_compatible(video: Video, other: VideoMetadata) -> bool:
  match other:
    case VideoProfile(codec, resolution, fps, level):
      _codec, _resolution, _fps, _level = video.video_profile

      return (
        _codec == codec and
        _resolution <= resolution and
        _fps <= fps and
        _level <= level
      )

    case AudioProfile(codec):
      return video.audio_profile.codec == codec

    case VideoCodec() as codec:
      return video.video_profile.codec == codec

    case AudioCodec() as codec:
      return video.audio_profile.codec == codec

  raise TypeError(type(other))


def profile_to_level(profile: str | None) -> float:
  if not (level := profile):
    return DEFAULT_LEVEL

  if PROFILE_SEP in level:
    name, level = level.split(PROFILE_SEP)

  if not level.isnumeric():
    return DEFAULT_LEVEL

  match level.split():
    case [val]:
      return float(val)

    case [big, small]:
      return float(f'{big}.{small}')

  return DEFAULT_LEVEL

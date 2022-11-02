from __future__ import annotations

from typing import Iterable, NamedTuple

from .base import get_name
from .codecs import AudioCodec, Codecs, Container, Subtitle, VideoCodec
from .profiles import AudioProfile, Profiles, VideoProfile, is_video_profile_compatible
from ..model.video import Video


VideoFormat = Codecs | Profiles | Container | Subtitle
VideoFormats = Iterable[VideoFormat]


class Formats(NamedTuple):
  container: Container | None = None
  video_profile: VideoProfile | None = None
  audio_profile: AudioProfile | None = None
  subtitle: Subtitle | None = None


def is_compatible(fmt: VideoFormat, other: VideoFormat) -> bool:
  match (fmt, other):
    case VideoProfile() as video_profile, VideoProfile() as other:
      return is_video_profile_compatible(video_profile, other)

    case AudioProfile(codec), AudioProfile(other):
      return other is codec

    case VideoCodec() as codec, VideoCodec() as other:
      return other is codec

    case AudioCodec() as codec, AudioCodec() as other:
      return other is codec

    case Container() as container, Container() as other:
      return other is container

    case Subtitle() as subtitle, Subtitle() as other:
      if not subtitle:
        return True

      return other is subtitle

  raise TypeError(f'Cannot compare {get_name(fmt)} with {get_name(other)}')
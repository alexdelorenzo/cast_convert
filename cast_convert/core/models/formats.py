from __future__ import annotations

from typing import Iterable, NamedTuple

from .codecs import AudioCodec, Container, Subtitle, VideoCodec
from .profiles import AudioProfile, VideoProfile


VideoProfiles = list[VideoProfile]
AudioProfiles = list[AudioProfile]
Containers = list[Container]
Subtitles = list[Subtitle]
Codecs = AudioCodec | VideoCodec
Profiles = AudioProfile | VideoProfile
VideoFormat = Codecs | Profiles | Container | Subtitle
VideoFormats = Iterable[VideoFormat]


class Formats(NamedTuple):
  container: Container | None = None
  video_profile: VideoProfile | None = None
  audio_profile: AudioProfile | None = None
  subtitle: Subtitle | None = None

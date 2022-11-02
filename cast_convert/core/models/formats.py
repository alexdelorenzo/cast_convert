from __future__ import annotations

from typing import Iterable, NamedTuple

from .codecs import Codecs, Container, Subtitle
from .profiles import AudioProfile, Profiles, VideoProfile


VideoFormat = Codecs | Profiles | Container | Subtitle
VideoFormats = Iterable[VideoFormat]


class Formats(NamedTuple):
  container: Container | None = None
  video_profile: VideoProfile | None = None
  audio_profile: AudioProfile | None = None
  subtitle: Subtitle | None = None

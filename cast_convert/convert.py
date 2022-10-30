from __future__ import annotations

from .base import VideoProfile, VideoCodec, AudioProfile, AudioCodec, Container, Formats
from .video import Video, VideoMetadata
from .device import Device


def transcode_video(video: Video, formats: Formats) -> Video:
  pass
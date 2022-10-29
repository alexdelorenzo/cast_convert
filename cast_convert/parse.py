from __future__ import annotations
from typing import Iterable

from yaml import safe_load

from .base import INFO, VideoProfile, VideoCodec


Yaml = dict[str, ...]


def get_yaml() -> Yaml:
  text = INFO.read_text()
  return safe_load(text)


def get_video_profiles(info: Yaml) -> Iterable[VideoProfile]:
  for codec in info:
    [name, attrs], *_ = codec.items()
    codec = VideoCodec.from_info(name)

    yield VideoProfile(
      codec=codec,
      resolution=attrs.get('resolution'),
      fps=float(attrs.get('fps')),
      level=float(attrs.get('level')),
    )

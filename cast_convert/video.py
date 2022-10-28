from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import NamedTuple, Literal, Final, \
  Iterable, Self, Generic, TypeVar, Any
from abc import ABC
from pathlib import Path
import logging

# from ffprobe import FFProbe
from pymediainfo import MediaInfo


PROFILE_SEP: Final[str] = '@L'


@dataclass
class Video:
  name: str
  path: Path
  container: str

  video: str
  profile: str
  width: int
  height: int
  fps: float

  audio: str

  data: MediaInfo

  @classmethod
  def from_path(cls, path: Path) -> Self:
    data: MediaInfo = MediaInfo.parse(path)

    [gen] = data.general_tracks
    [video] = data.video_tracks
    audio, *_ = data.audio_tracks

    title = gen.complete_name
    container = Container.from_info(gen.format)
    codec = Codec.from_info(video.format)
    height, width = video.height, video.width
    audio_codec = audio.codec_id_hint
    fps = video.original_frame_rate
    profile = video.format_profile

    return cls(
      name=title,
      path=path.absolute(),
      video=codec,
      container=container,
      width=width,
      height=height,
      audio=audio_codec,
      fps=fps,
      profile=profile,
      data=data,
    )

  @property
  def level(self) -> float | None:
    if not level := self.profile:
      return None

    if PROFILE_SEP in level:
      name, level = level.split(PROFILE_SEP)

    if not level.isnumeric():
      return None

    match level.split():
      case [_]:
        return float(level)

      case [big, little]:
        return float(f'{big}.{small}')

    return None


def normalize_info(info: str) -> str:
  info = info.casefold()
  return ''.join(char for char in info if char.isalnum())

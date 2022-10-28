from dataclasses import dataclass, field
from enum import StrEnum
from typing import NamedTuple, Literal, Final, Iterable
from abc import ABC
from pathlib import Path
import logging

from yaml import safe_load


INFO: Final[Path] = Path('../chromecasts.yml')


Yaml = dict[str, ...]


class CastConvertException(Exception):
  pass


class VideoError(CastConvertException):
  pass


class UnknownCodec(VideoError):
  pass


class Normalize:
  @classmethod
  def _missing_(cls, value: str) -> Self:
    logging.info(f"Couldn't find {value}")
    return cls.unknown

  @classmethod
  def from_info(cls, info: str) -> Self:
    normalized = normalize_info(info)
    return cls(normalized)


class Container(Normalize, StrEnum):
  mp2t: str = auto()
  mp3: str = auto()
  mp4: str = auto()
  mpeg4: str = auto()
  ogg: str = auto()
  wav: str = auto()
  webm: str = auto()
  matroska: str = auto()

  unknown: str = auto()


class Codec(Normalize, StrEnum):
  avc: str = auto()
  mpeg4: str = auto()
  h264: str = auto()
  h265: str = auto()
  hevc: str = auto()
  vp8: str = auto()
  vp9: str = auto()

  aac: str = auto()
  eacs: str = auto()
  flac: str = auto()
  heaac: str = auto()
  lcaac: str = auto()
  opus: str = auto()
  vorbis: str = auto()
  wav: str = auto()
  webm: str = auto()

  unknown: str = auto()


@dataclass(eq=True, frozen=True)
class BaseCodec(ABC):
  name: str


@dataclass(eq=True, frozen=True)
class AudioCodec(BaseCodec):
  pass


@dataclass(eq=True, frozen=True)
class VideoCodec(BaseCodec):
  resolution: int
  fps: float = 30
  level: float = 0.0
  codec: Codec = Codec.unknown


@dataclass
class Device:
  name: str

  video: set[VideoCodec] = field(default_factory=set)
  audio: set[AudioCodec] = field(default_factory=set)

  containers: set[str] = field(default_factory=set)

  def add_codec(codec: Codec):
    match codec:
      case VideoCodec():
        self.video.append(codec)

      case AudioCodec():
        self. audio.append(codec)

      case _:
        raise TypeError("Not a Codec: {codec}")


def get_yaml() -> Yaml:
  text = INFO.read_text()
  return safe_load(text)


def get_video_codecs(info: Yaml) -> Iterable[Codec]:
  for codec in info:
    [name, attrs], *_ = codec.items()
    codec = Codec.from_info(name)

    yield VideoCodec(
      name,
      attrs.get('resolution'),
      attrs.get('fps'),
      attrs.get('level'),
      codec=codec,
    )


def get_device(name: str, device_info: Yaml, data: Yaml) -> Device:
  audio = set(map(AudioCodec, data['audio']))
  video = set(get_video_codecs(device_info['codecs']))
  containers = data['containers']

  return Device(name, video, audio, containers)


def get_devices(data: Yaml) -> Iterable[Device]:
  for name, device_info in data['devices'].items():
    yield get_device(name, device_info, data)


def is_compatible(video: Video, codec: BaseCodec) -> bool:
  pass


if __name__ == "__main__":
  data = get_yaml()
  devices = list(get_devices(data))
  print(devices)

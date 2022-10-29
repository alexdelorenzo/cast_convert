from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable

from .base import VideoProfile, AudioProfile, Profile, Container, \
  AudioCodec, UnknownCodec, VideoCodec
from .parse import get_video_profiles, Yaml
from .video import Video


@dataclass
class Device:
  name: str

  video_profiles: set[VideoProfile] = field(default_factory=set)
  audio_profiles: set[AudioProfile] = field(default_factory=set)

  containers: set[Container] = field(default_factory=set)

  def add_profile(self, profile: Profile):
    match profile:
      case VideoProfile() as profile:
        self.video_profiles.add(profile)

      case AudioProfile() as profile:
        self.audio_profiles.add(profile)

      case Container() as container:
        self.containers.add(container)

      case _:
        raise TypeError(f"Not encodable: {profile}")

  def can_play(self, video: Video) -> bool:
    if video.video_profile.codec == VideoCodec.unknown or video.audio_profile.codec == AudioCodec.unknown:
      raise UnknownCodec(f"Missing codec for {video}")

    can_video = any(video.is_compatible(profile) for profile in self.video_profiles)
    can_audio = any(video.is_compatible(profile) for profile in self.audio_profiles)

    return can_video and can_audio


def get_device(name: str, device_info: Yaml, data: Yaml) -> Device:
  names = map(AudioCodec.from_info, data['audio'])

  audio = set(map(AudioProfile, names))
  video = set(get_video_profiles(device_info['codecs']))
  containers = set(map(Container.from_info, data['containers']))

  return Device(name, video, audio, containers)


def get_devices(data: Yaml) -> Iterable[Device]:
  for name, device_info in data['devices'].items():
    yield get_device(name, device_info, data)

from __future__ import annotations
from typing import TYPE_CHECKING

from .models.profiles import AudioProfile, VideoProfile
from .models.formats import Formats
from .models.codecs import Container, Subtitle
from .video import Video

if TYPE_CHECKING:
  from .device import Device


def transcode_video(
  device: Device,
  video: Video,
  default_video: VideoProfile | None = None,
) -> VideoProfile | None:
  if device.can_play_video(video):
    return None

  _, video_profile, *_ = video.formats

  if not default_video:
    default_video, *_ = device.video_profiles

  return transcode_video_profile(video_profile, default_video)


def transcode_audio(
  device: Device,
  video: Video,
  default_audio: AudioProfile | None = None,
) -> AudioProfile | None:
  if device.can_play_audio(video):
    return None

  *_, audio_profile, _ = video.formats

  if not default_audio:
    default_audio, *_ = device.audio_profiles

  return transcode_audio_profile(audio_profile, default_audio)


def transcode_container(
  device: Device,
  video: Video,
  default_container: Container | None = None,
) -> Container | None:
  if device.can_play_container(video):
    return None

  container, *_ = video.formats

  if not default_container:
    default_container, *_ = device.containers

  return transcode_containers(container, default_container)


def transcode_subtitle(
  device: Device,
  video: Video,
  default_subtitle: Subtitle | None = None,
) -> Subtitle | None:
  if device.can_play_subtitle(video):
    return None

  *_, subtitle = video.formats

  if not default_subtitle:
    default_subtitle, *_ = device.subtitles

  return transcode_subtitles(subtitle, default_subtitle)


def transcode_to(
  device: Device,
  video: Video,
  default_video: VideoProfile | None = None,
  default_audio: AudioProfile | None = None,
  default_container: Container | None = None,
  default_subtitle: Subtitle | None = None,
) -> Formats | None:
  if device.can_play(video):
    return None

  new_video = transcode_video(device, video, default_video)
  new_audio = transcode_audio(device, video, default_audio)
  new_container = transcode_container(device, video, default_container)
  new_subtitle = transcode_subtitle(device, video, default_subtitle)

  return Formats(
    container=new_container,
    video_profile=new_video,
    audio_profile=new_audio,
    subtitle=new_subtitle,
  )


def transcode_video_profile(
  video_profile: VideoProfile,
  default_video: VideoProfile,
) -> VideoProfile:
  codec, resolution, fps, level = video_profile
  default_codec, default_resolution, default_fps, default_level = default_video

  new_codec = None if codec is default_codec else default_codec
  new_resolution = None if resolution <= default_resolution else default_resolution
  new_fps = None if fps <= default_fps else default_fps

  new_level = None if level <= default_level else default_level
  new_level = new_level if new_codec is None else None

  return VideoProfile(
    codec=new_codec,
    resolution=new_resolution,
    fps=new_fps,
    level=new_level,
  )


def transcode_audio_profile(
  audio_profile: AudioProfile,
  default_audio: AudioProfile,
) -> AudioProfile:
  [codec] = audio_profile
  new_codec = None if codec is default_audio.codec else default_audio.codec

  return AudioProfile(new_codec)


def transcode_containers(
  container: Container,
  default_container: Container,
) -> Container | None:
  return None if container is default_container else default_container


def transcode_subtitles(
  subtitle: Subtitle,
  default_subtitle: Subtitle,
) -> Subtitle | None:
  return None if subtitle is default_subtitle else default_subtitle


def transcode_formats(formats: Formats, to_formats: Formats) -> Formats | None:
  if formats == to_formats:
    return None

  container, video_profile, audio_profile, subtitle = formats
  to_container, to_video, to_audio, to_subtitle = to_formats

  new_container = transcode_containers(container, to_container)
  new_video = transcode_video_profile(video_profile, to_video)
  new_audio = transcode_audio_profile(audio_profile, to_audio)
  new_subtitle = transcode_subtitle(subtitle, to_subtitle)

  return Formats(
    container=new_container,
    video_profile=new_video,
    audio_profile=new_audio,
    subtitle=new_subtitle,
  )
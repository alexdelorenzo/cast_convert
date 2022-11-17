from __future__ import annotations

from typing import Any, Final, Iterable, TYPE_CHECKING, cast
from operator import itemgetter
import logging

from rich import print

from ..base import esc, first
from ..media.base import get_name
from ..media.formats import Formats
from ..media.profiles import AudioProfile, Profile, VideoProfile, is_codec_compatible, \
  is_fps_compatible, is_level_compatible, is_resolution_compatible
from ..model.video import Video


if TYPE_CHECKING:
  from ..media.codecs import Container, Subtitle
  from ..model.device import Device

SCORE_INDEX: Final[int] = 1


Score = int
ProfileScore = tuple[Profile, Score]
ProfileScores = Iterable[ProfileScore]
ScoreMap = dict[Profile, Score]


compare_score = itemgetter(SCORE_INDEX)


def exists(*items: Any) -> bool:
  return all(item is not None for item in items)


def transcode_video(
  device: Device,
  video: Video,
  default_video: VideoProfile | None = None,
) -> VideoProfile | None:
  if device.can_play_video(video):
    return None

  _, video_profile, *_ = video.formats

  if not default_video:
    default_video = get_default_video_profile(device, video)

  return transcode_video_profile(video_profile, default_video)


def get_default_video_profile(device: Device, video: Video) -> VideoProfile | None:
  vid_prof = video.formats.video_profile

  scores: ScoreMap = {
    prof: prof.count
    for dev_prof in device.video_profiles
    if (prof := transcode_video_profile(vid_prof, dev_prof))
  }

  if not scores:
    logging.info(f'Choosing first {get_name(VideoProfile)} from {device.name}')
    return first(device.video_profiles)

  profile_scores = cast(ProfileScores, scores.items())
  profile_scores = sorted(profile_scores, key=compare_score)
  profile, score = first(profile_scores)

  return profile


def transcode_audio(
  device: Device,
  video: Video,
  default_audio: AudioProfile | None = None,
) -> AudioProfile | None:
  if device.can_play_audio(video):
    return None

  *_, audio_profile, _ = video.formats

  if not default_audio:
    logging.info(f'Choosing first {get_name(AudioProfile)} from {device.name}')
    default_audio = first(device.audio_profiles)

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
    logging.info(f'Choosing first {get_name(Container)} from {device.name}')
    default_container = first(device.containers)

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
    logging.info(f'Choosing first {get_name(Subtitle)} from {device.name}')
    default_subtitle = first(device.subtitles)

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

  new_codec = new_resolution = new_fps = new_level = None

  if exists(codec, default_codec):
    new_codec = None if is_codec_compatible(codec, default_codec) else default_codec

  if exists(resolution, default_resolution):
    new_resolution = None if is_resolution_compatible(resolution, default_resolution) else default_resolution

  if exists(fps, default_fps):
    new_fps = None if is_fps_compatible(fps, default_fps) else default_fps

  if new_codec:
    new_level = default_level

  elif exists(level, default_level):
    new_level = None if is_level_compatible(level, default_level) else default_level

  return VideoProfile(
    codec=new_codec,
    resolution=new_resolution,
    fps=new_fps,
    level=new_level,
  )


def transcode_audio_profile(
  audio_profile: AudioProfile | None,
  default_audio: AudioProfile | None,
) -> AudioProfile | None:
  if not exists(audio_profile, default_audio):
    return None

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
  new_subtitle = transcode_subtitles(subtitle, to_subtitle)

  return Formats(
    container=new_container,
    video_profile=new_video,
    audio_profile=new_audio,
    subtitle=new_subtitle,
  )


def should_transcode(
  device: Device,
  video: Video,
) -> bool:
  if not device:
    return False

  if device.can_play(video):
    print(f'[green][✅] File [b blue]"{esc(video.path)}"[/] is compatible with [b]{device.name}[/].')
    return False

  return True



from __future__ import annotations

from typing import Final

from .base import VideoProfile, VideoCodec, AudioProfile, AudioCodec, Container, Formats, \
  Extension
from .exceptions import UnknownFormat
from .video import Video, VideoMetadata
from .device import Device

import ffmpeg


DEFAULT_EXT: Final[Extension] = Container.matroska.to_extension()


def transcode_video(video: Video, formats: Formats) -> Video:
  container, video_profile, audio_profile = video.formats
  video_codec, resolution, fps, level = video_profile
  [audio_codec] = audio_profile

  _, video_profile, audio_profile = formats

  if formats.container:
    try:
      new_ext = formats.container.to_extension()

    except UnknownFormat as e:
      new_ext = DEFAULT_EXT

  else:
    new_ext = video.path.suffix

  new_path = (
    video.path
    .with_stem(f'{video.path.stem}_transcoded')
    .with_suffix(new_ext)
  )

  args: dict[str, str] = {}

  if formats.audio_profile.codec:
    args['acodec'] = 'copy'

  else:
    args['acodec'] = ''

  if formats.video_profile.codec:
    args['vcodec'] = 'copy'

  stream = (
    ffmpeg
    .input(video.path)
    .output(new_path, **args)
  )
  stream.run()

  raise NotImplementedError("Not done yet")
  return Video.from_path(new_path)
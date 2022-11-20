from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

from .codecs import AudioCodec, Codecs, Container, Subtitle, VideoCodec
from .profiles import AudioProfile, Profile, Profiles, VideoProfile, is_video_profile_compatible
from ..base import HasName, NEW_LINE, get_name, has_items


VideoFormat = Codecs | Profiles | Container | Subtitle
VideoFormats = Iterable[VideoFormat]


class Formats(NamedTuple):
  container: Container | None = None
  video_profile: VideoProfile | None = None
  audio_profile: AudioProfile | None = None
  subtitle: Subtitle | None = None

  def __bool__(self) -> bool:  # Protocol: HasItems
    return has_items(self)

  def is_compatible(self, other: Metadata) -> bool:  # Protocol: IsCompatible
    return is_compatible(self, other)

  @property
  def as_dict(self) -> dict[str, Metadata]:  # Protocol: AsDict
    return self._asdict()

  @property
  def text(self) -> str:  # Protocol: AsText
    lines = list[str]()

    for name, val in self.as_dict.items():
      match val:
        case Profile() as profile:
          lines.append(profile.text)

        case HasName():
          lines.append(f'[b]{val.name}[/]: [b blue]{val}[/]')

        case None:
          pass

        case _:
          lines.append(f'[b]{name.title()}[/]: [b blue]{val}[/]')

    return NEW_LINE.join(lines)

  @property
  def count(self) -> int:
    container, *profiles, sub = self

    count = sum(val is not None for val in (container, sub))
    count += sum(prof.count for prof in profiles if prof)

    return count

  @property
  def weight(self) -> int:
    container, *profiles, sub = self

    count = sum(val is not None for val in (container, sub))
    count += sum(prof.weight for prof in profiles if prof)

    return count


Metadata = VideoFormat | Formats


def are_compatible(metadata: Metadata, other: Metadata) -> bool:
  match metadata, other:
    case VideoProfile() as video_profile, VideoProfile() as other:
      return is_video_profile_compatible(video_profile, other)

    case AudioProfile(codec), AudioProfile(other):
      return other is codec

    case VideoCodec() as codec, VideoCodec() as other:
      return other is codec

    case AudioCodec() as codec, AudioCodec() as other:
      return other is codec

    case Container() as container, Container() as other:
      return other is container

    case Subtitle() as subtitle, Subtitle() as other:
      if not subtitle or not other:
        return True

      return other is subtitle

    case Formats() as formats, Formats() as other:
      return are_fmts_compatible(formats, other)

    case None, None:
      return True

    case (_, None) | (None, _):
      return False

  raise TypeError(f'Cannot compare {get_name(metadata)} with {get_name(other)}')


FormatPairs = Iterable[tuple[VideoFormat, VideoFormat]]


def are_fmts_compatible(formats: Formats, other: Formats) -> bool:
  both: FormatPairs = zip(formats, other)

  return all(are_compatible(fmt, _fmt) for fmt, _fmt in both)


def is_compatible(formats: Formats, other: Metadata) -> bool:
  container, video_profile, audio_profile, subtitle = formats

  match other:
    case VideoProfile() as profile:
      return are_compatible(video_profile, profile)

    case AudioProfile(codec):
      return are_compatible(audio_profile.codec, codec)

    case VideoCodec() as codec:
      return are_compatible(video_profile.codec, codec)

    case AudioCodec() as codec:
      return are_compatible(audio_profile.codec, codec)

    case Container() as _container:
      return are_compatible(container, _container)

    case Subtitle() as _subtitle:
      if not _subtitle or not subtitle:
        return True

      return are_compatible(subtitle, _subtitle)

    case Formats() as _formats:
      return are_compatible(formats, _formats)

  raise TypeError(f'Cannot compare formats with {get_name(other)}')

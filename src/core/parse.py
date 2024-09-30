from __future__ import annotations

from pathlib import Path
from typing import Any, Final

from yaml import safe_load


ASSET_DIRNAME: Final[str] = 'assets'
SUPPORT_FILENAME: Final[str] = 'support.yml'

CORE_DIR: Final[Path] = Path(__file__).parent.absolute()
SOURCE_DIR: Final[Path] = CORE_DIR.parent.absolute()
ASSET_DIR: Final[Path] = SOURCE_DIR / ASSET_DIRNAME

DEVICE_INFO: Final[Path] = ASSET_DIR / SUPPORT_FILENAME
SUPPORT_INFO: Final[Path] = ASSET_DIR / SUPPORT_FILENAME


type Fmt = str
type Alias = str
type Extension = str

type Fmts = list[Fmt]
type Aliases = list[Alias]
type FmtAliases = dict[Fmt, Aliases]
type AliasFmts = dict[Alias, Fmt]

type FmtExtensions = dict[Fmt, Extension]
type FfmpegCodecs = dict[str, FmtAliases]

type Yaml = dict[str, Any] | list[Yaml] | dict[str, Yaml]


def get_yaml(path: Path = DEVICE_INFO) -> Yaml:
  text = path.read_text()
  return safe_load(text)


DEVICE_DATA: Final[Yaml] = get_yaml()

EXTENSIONS: Final[FmtExtensions] = DEVICE_DATA['extensions']

ENCODERS: Final[FfmpegCodecs] = DEVICE_DATA['encoders']
VIDEO_ENCODERS: Final[FmtAliases] = ENCODERS['video']
AUDIO_ENCODERS: Final[FmtAliases] = ENCODERS['audio']
SUBTITLE_ENCODERS: Final[FmtAliases] = ENCODERS['subtitles']

DECODERS: Final[FfmpegCodecs] = DEVICE_DATA['decoders']
SUBTITLES: Final[Fmts] = DEVICE_DATA['subtitles']
CONTAINERS: Final[Fmts] = DEVICE_DATA['containers']
AUDIO: Final[Fmts] = DEVICE_DATA['audio']
DEVICES: Final[Yaml] = DEVICE_DATA['devices']

FMT_ALIASES: Final[FmtAliases] = DEVICE_DATA['aliases']
ALIAS_FMTS: Final[AliasFmts] = {
  alias: fmt
  for fmt, aliases in FMT_ALIASES.items()
  for alias in aliases
}

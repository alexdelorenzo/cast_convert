from __future__ import annotations
from pathlib import Path
from typing import Final

from yaml import safe_load


SRC_DIR: Final[Path] = Path(__file__).parent.absolute()
ASSET_DIR: Final[Path] = SRC_DIR / 'assets'
DEVICE_INFO: Final[Path] = ASSET_DIR / 'support.yml'
SUPPORT_INFO: Final[Path] = ASSET_DIR / 'support.yml'


Fmt = str
Alias = str
Extension = str

Aliases = list[Alias]
FmtAliases = dict[Fmt, Aliases]
AliasFmts = dict[Alias, Fmt]

FmtNames = list[Fmt]
FmtExtensions = dict[Fmt, Extension]

Yaml = dict[str, ...] | list['Yaml'] | dict[str, 'Yaml']


def get_yaml(path: Path = DEVICE_INFO) -> Yaml:
  text = path.read_text()
  return safe_load(text)


DEVICE_DATA: Final[Yaml] = get_yaml()

EXTENSIONS: Final[FmtExtensions] = DEVICE_DATA['extensions']
ENCODERS: Final[FmtAliases] = DEVICE_DATA['encoders']
DECODERS: Final[FmtAliases] = DEVICE_DATA['decoders']
SUBTITLES: Final[FmtNames] = DEVICE_DATA['subtitles']
CONTAINERS: Final[FmtNames] = DEVICE_DATA['containers']
AUDIO: Final[FmtNames] = DEVICE_DATA['audio']
DEVICES: Final[Yaml] = DEVICE_DATA['devices']

FMT_ALIASES: Final[FmtAliases] = DEVICE_DATA['aliases']
ALIAS_FMTS: Final[AliasFmts] = {
  alias: fmt
  for fmt, aliases in FMT_ALIASES.items()
  for alias in aliases
}

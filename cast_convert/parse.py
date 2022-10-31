from __future__ import annotations
from pathlib import Path
from typing import Final

from yaml import safe_load


SRC_DIR: Final[Path] = Path(__file__).parent.parent.absolute()
DEVICE_INFO: Final[Path] = SRC_DIR / 'device-support.yml'


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


DATA: Final[Yaml] = get_yaml()

EXTENSIONS: Final[FmtExtensions] = DATA['extensions']
ENCODERS: Final[FmtAliases] = DATA['encoders']
DECODERS: Final[FmtAliases] = DATA['decoders']
SUBTITLES: Final[FmtNames] = DATA['subtitles']

FMT_ALIASES: Final[FmtAliases] = DATA['aliases']
ALIAS_FMTS: Final[AliasFmts] = {
  alias: fmt
  for fmt, aliases in FMT_ALIASES.items()
  for alias in aliases
}

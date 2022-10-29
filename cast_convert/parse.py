from __future__ import annotations

from pathlib import Path
from typing import Final

from yaml import safe_load


SRC_DIR: Final[Path] = Path(__file__).parent.parent.absolute()
DEVICE_INFO: Final[Path] = SRC_DIR / 'device-support.yml'


Fmt = str
Alias = str
Aliases = list[Alias]
Yaml = dict[str, ...]


def get_yaml(path: Path = DEVICE_INFO) -> Yaml:
  text = path.read_text()
  return safe_load(text)


DATA: Final[Yaml] = get_yaml()
ALIASES: Final[dict[Fmt, Aliases]] = DATA['aliases']

INVERSED_ALIASES: Final[dict[Alias, Fmt]] = {
  alias: fmt for fmt, aliases in ALIASES.items()
  for alias in aliases
}

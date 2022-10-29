from __future__ import annotations

from pathlib import Path
from typing import Final

from yaml import safe_load


Yaml = dict[str, ...]

DEVICE_INFO: Final[Path] = Path('chromecasts.yml').absolute()


def get_yaml(path: Path = DEVICE_INFO) -> Yaml:
  text = path.read_text()
  return safe_load(text)


DATA: Final[Yaml] = get_yaml()
ALIASES: Final[dict[str, list[str]]] = DATA['aliases']
INVERSED_ALIASES: Final[dict[str, str]] = \
  {val: key for key, vals in ALIASES.items() for val in vals}



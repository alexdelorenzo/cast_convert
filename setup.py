from __future__ import annotations

from pathlib import Path
from typing import Final

from setuptools import find_packages, setup

from cast_convert import AUTHOR_INFO, DESCRIPTION, ENTRY_POINTS, \
  LICENSE, NAME, PROJECT_HOME, __version__


REQUIREMENTS: list[str] = (
  Path('requirements.txt')
  .read_text()
  .split('\n')
)
REQUIREMENTS = [
  rule
  for req in REQUIREMENTS
  if (rule := req.strip()) and not rule.startswith('#')
]

ASSET_DIRS: Final[list[str]] = [
  'assets/*.yml',
]

PKG_DATA: Final[dict[str, list[str]]] = {
  NAME: ASSET_DIRS
}

PYTHON_VERSION: str = '>=3.12'

setup(
  name=NAME,
  version=__version__,
  description=DESCRIPTION,
  url=PROJECT_HOME,
  author=AUTHOR_INFO,
  license=LICENSE,
  packages=[*find_packages()],
  package_data=PKG_DATA,
  zip_safe=True,
  install_requires=REQUIREMENTS,
  keywords='chromecast transcode convert video cli'.split(' '),
  entry_points=ENTRY_POINTS,
  python_requires=PYTHON_VERSION,
)

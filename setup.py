from __future__ import annotations
from sys import version_info
from pathlib import Path
from typing import Final

from setuptools import setup, find_packages

from cast_convert import NAME, __version__
from cast_convert.core.base import DESCRIPTION


REQUIREMENTS: list[str] = (
  Path('requirements.txt')
  .read_text()
  .split('\n')
)
REQUIREMENTS = [req for req in REQUIREMENTS if req]

ASSET_DIRS: Final[list[str]] = [
  'assets/*.yml',
]

PKG_DATA: Final[dict[str, list[str]]] = {
  NAME: ASSET_DIRS
}

setup(
  name=NAME,
  version=__version__,
  description=DESCRIPTION,
  url="https://github.com/alexdelorenzo/cast_convert",
  author="Alex DeLorenzo (alexdelorenzo.dev)",
  license="AGPL 3.0",
  packages=[*find_packages()],
  package_data=PKG_DATA,
  zip_safe=True,
  install_requires=REQUIREMENTS,
  keywords='chromecast transcode convert video cli'.split(' '),
  entry_points={
    "console_scripts": [
      "cast-convert = cast_convert.cli:app",
    ]
  }
)

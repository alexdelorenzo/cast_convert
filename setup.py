from __future__ import annotations
from sys import version_info
from pathlib import Path
from typing import Final

from setuptools import setup, find_packages

from cast_convert import __version__


NAME: Final[str] = 'cast_convert'
MIN_PYTHON_VERSION: Final[tuple[int, ...]] = (3, 11)
OLD_PYTHON_REQUIREMENTS: Final[list[str]] = ['mypy-lang']

REQUIREMENTS: Final[list[str]] = (
  Path('requirements.txt')
  .read_text()
  .split('\n')
)

ASSET_DIRS: Final[list[str]] = [
  'assets/*.yml',
]

PKG_DATA: Final[dict[str, list[str]]] = {
  NAME: ASSET_DIRS
}


if version_info < MIN_PYTHON_VERSION:
  REQUIREMENTS.extend(OLD_PYTHON_REQUIREMENTS)


setup(
  name="cast_convert",
  version=__version__,
  description="📽️ Identify and convert videos to formats that are Chromecast supported.",
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
      "cast_convert = cast_convert.old:cmd",
      "cast-convert = cast_convert.cli.orig:app",
    ]
  }
)

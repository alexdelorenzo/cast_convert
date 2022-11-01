from setuptools import setup
from sys import version_info
from pathlib import Path

from cast_convert import __version__


MIN_PYTHON_VERSION = (3, 11)
OLD_PYTHON_REQUIREMENTS = ['mypy-lang']

REQUIREMENTS = Path('requirements.txt').read_text().split('\n')


if version_info < MIN_PYTHON_VERSION:
  REQUIREMENTS.extend(OLD_PYTHON_REQUIREMENTS)

setup(
  name="cast_convert",
  version=__version__,
  description="Identify and convert videos to formats that are Chromecast supported.",
  url="https://github.com/alexdelorenzo/cast_convert",
  author="alexdelorenzo.dev (Alex DeLorenzo)",
  license="AGPL 3.0",
  packages=['cast_convert'],
  zip_safe=True,
  install_requires=REQUIREMENTS,
  keywords='chromecast transcode convert video cli'.split(' '),
  entry_points={"console_scripts": ["cast_convert = cast_convert.old:cmd"]}
)

from setuptools import setup
from sys import version_info


MIN_PYTHON_VERSION = (3, 5)
OLD_PYTHON_REQUIREMENTS = ['mypy-lang']

with open('requirements.txt', 'r') as file:
    requirements = file.readlines()

if version_info < MIN_PYTHON_VERSION:
    requirements.extend(OLD_PYTHON_REQUIREMENTS)

setup(name="cast_convert",
      version="0.1.4.3",
      description="Convert and inspect video for Chromecast playback",
      url="https://github.com/thismachinechills/cast_convert",
      author="thismachinechills (Alex)",
      license="AGPL 3.0",
      packages=['cast_convert'],
      zip_safe=True,
      install_requires=requirements,
      keywords=["chromecast", "ffmpeg", "transcode"],
      entry_points={"console_scripts": ["cast_convert = cast_convert.convert:cmd"]})

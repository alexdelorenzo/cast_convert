from setuptools import setup


setup(name="cast_convert",
      version="0.1.2",
      description="Convert and inspect video for Chromecast playback",
      url="https://github.com/thismachinechills/cast_convert",
      author="thismachinechills (Alex)",
      license="AGPL 3.0",
      packages=['cast_convert'],
      zip_safe=True,
      install_requires=["click"],
      keywords=["chromecast", "ffmpeg", "transcode"],
      entry_points={"console_scripts": ["cast_convert = cast_convert.convert:cmd"]}
      )

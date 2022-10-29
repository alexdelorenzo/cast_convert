from __future__ import annotations


class CastConvertException(Exception):
    pass


class StreamNotFoundException(CastConvertException):
    pass


class VideoError(CastConvertException):
  pass


class UnknownCodec(VideoError):
  pass

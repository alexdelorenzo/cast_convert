from __future__ import annotations


class CastConvertException(Exception):
  pass


class StreamNotFoundException(CastConvertException):
  pass


class VideoError(CastConvertException):
  pass


class UnknownFormat(VideoError):
  pass


class DeviceError(CastConvertException):
  pass

from __future__ import annotations


class CastConvertException(Exception):
  pass


class StreamNotFoundException(CastConvertException):
  pass


class FormatError(CastConvertException, ValueError):
  pass


class CannotCompare(CastConvertException, TypeError):
  pass


class UnknownFormat(FormatError):
  pass


class FileNotVideo(FormatError):
  pass


class DeviceError(CastConvertException):
  pass

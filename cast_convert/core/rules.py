from .media.base import OnTranscodeErr
from .media.codecs import Codecs
from .parse import ENCODERS, Aliases


def remove_encoder(codec: Codecs):
  aliases: Aliases

  match ENCODERS.get(codec):
    case []:
      pass

    case None:
      pass

    case list() as aliases:
      aliases.pop()

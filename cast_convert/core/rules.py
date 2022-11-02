from .models.base import OnTranscodeErr
from .models.formats import Codecs
from .parse import ENCODERS, Aliases


def remove_encoder(codec: Codecs):
  aliases: Aliases

  match ENCODERS.get(codec):
    case []:
      pass

    case None:
      pass

    case aliases:
      aliases.pop()

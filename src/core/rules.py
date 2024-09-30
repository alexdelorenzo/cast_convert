from .media.codecs import Codecs
from .parse import Aliases, ENCODERS


def remove_encoder(codec: Codecs):
  aliases: Aliases

  match ENCODERS.get(codec):
    case []:
      pass

    case None:
      pass

    case list() as aliases:
      aliases.pop()

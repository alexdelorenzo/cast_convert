from __future__ import annotations
from typing import Final


__version__: Final[str] = '0.13.0'

NAME: Final[str] = 'cast_convert'
PROJECT_HOME: Final[str] = 'https://github.com/alexdelorenzo/cast_contvert'
AUTHOR_HOME: Final[str] = 'https://alexdelorenzo.dev'
AUTHOR: Final[str] = 'Alex DeLorenzo'
AUTHOR_INFO: Final[str] = f'{AUTHOR} ({AUTHOR_HOME})'
COPYRIGHT_NOTICE: Final[str] = f'Copyright © 2023 [b]{AUTHOR_INFO}[/b]'
LICENSE: Final[str] = 'CC BY-NC-ND 4.0'

DESCRIPTION: Final[str] = \
  "📽️ Identify and convert videos to formats that are Chromecast supported."

CMD: Final[str] = 'cast-convert'
CLI_MODULE: Final[str] = f'{NAME}.cli'
CLI_ENTRY: Final[str] = 'cli'

ENTRY_POINTS: Final[dict[str, list[str]]] = {
  "console_scripts": [
    f"{CMD} = {CLI_MODULE}:{CLI_ENTRY}",
  ]
}

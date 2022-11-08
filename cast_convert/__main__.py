import logging

import typer

from .cli.commands import app


logging.basicConfig(level=logging.WARN)

app()

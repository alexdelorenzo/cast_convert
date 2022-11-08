import logging

import typer

from .cli.orig import app


logging.basicConfig(level=logging.WARN)

app()

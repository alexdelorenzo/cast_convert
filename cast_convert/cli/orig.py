from __future__ import annotations

from pathlib import Path
from typing import Final

from typer import Typer, Option, Argument

from .helpers import DEFAULT_MODEL, _get_command


app: Final[Typer] = Typer()


@app.command(help='Get FFMPEG transcoding command.')
def get_command(
  name: str = Option(DEFAULT_MODEL, help='Chromecast model name'),
  paths: list[Path] = Argument(None, help='Path to video', resolve_path=True),
):
  for path in paths:
    _get_command(name, path)

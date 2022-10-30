#!/usr/bin/env python3
from __future__ import annotations
from .old.cmd import cmd

import click


__version__ = '0.1.7.19'


@click.command(help="Print version")
def version():
    print(__version__)


cmd.add_command(version)

from .old.watch import *
from .old.convert import *
from .old.media_info import *
from . import *




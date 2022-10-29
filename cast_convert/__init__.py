#!/usr/bin/env python3

__version__ = '0.1.7.19'


from .old.cmd import cmd as command
import click

@click.command(help="Print version")
def version():
    print(__version__)


command.add_command(version)

from .old.watch import *
from .old.convert import *
from .old.media_info import *
from . import *




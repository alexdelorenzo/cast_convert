#!/usr/bin/env python3

__version__ = '0.1.7.19'


from .cmd import cmd as command
import click

@click.command(help="Print version")
def version():
    print(__version__)


command.add_command(version)

from .watch import *
from .convert import *
from .media_info import *
from . import *




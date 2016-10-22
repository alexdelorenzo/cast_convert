#!/usr/bin/env python3

__version__ = '0.1.7.17'


from .cmd import cmd as command
from .watch import *
from . import *
from .convert import *
from .media_info import *

import click


@click.command(help="Print version")
def version():
    print(__version__)


command.add_command(version)

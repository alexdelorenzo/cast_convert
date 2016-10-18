__version__ = '0.1.5.19'


from .cmd import cmd as command
from .watch import *
from . import *
from .convert import *
from .media_info import *


@click.command(help="Print version")
def version():
    print(__version__)


command.add_command(version)

from .. import CLI_ENTRY, CLI_MODULE
from .commands import cli


# ensure entrypoints have correct names
assert __name__ == CLI_MODULE, __name__
assert cli.info.name == CLI_ENTRY, cli.info.name

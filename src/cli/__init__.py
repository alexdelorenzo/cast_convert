from .. import CLI_ENTRY, CLI_MODULE
from .commands import cli


# ensure entrypoints have correct names
assert __name__ == CLI_MODULE, f"{__name__=} is not {CLI_MODULE=}"
assert cli.info.name == CLI_ENTRY, f"{cli.info.name=} is not {CLI_ENTRY=}"

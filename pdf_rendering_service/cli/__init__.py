"""
The package contains general CLI that allows to run both api server and dramatiq actor
"""

import importlib
from sys import argv as sys_argv, exit as sys_exit
from typing import Optional, List, Type, Dict

from pdf_rendering_service.base import get_logger
log = get_logger("pdf_rendering_service.cli")

from .command import Command

commands: Dict[str, Type[Command]] = {}
for cli_module in ["pdf_rendering_service.api.cli", "pdf_rendering_service.pdf_processor.cli"]:
    try:
        commands.update(getattr(importlib.import_module(cli_module), "options"))
    except ImportError as ex:
        log.error(f"Can't import commands from {cli_module}. Exception: {ex}")


def main(argv: Optional[List[str]] = None) -> None:
    """
    :param argv: Command line arguments
    """
    if not argv:
        argv = sys_argv

    while True:  # pragmatic loop allowing for breaks
        if len(argv) < 2:
            break

        command = commands.get(argv[1])
        if command is None:
            break

        sys_exit(command(argv).execute())  # pragmatic loop terminates

    # Wrong execution, display (top-level) usage
    cmds = "\n  ".join(sorted([
            f"{cmd_name.ljust(15)}{cmd.description}"
            for cmd_name, cmd in commands.items()]))
    command_name = argv[0]
    print(f"""usage: {command_name} COMMAND OPTION*

commands:
  {cmds}

Run {command_name} COMMAND -h to get command OPTIONS help.""")
    sys_exit(1)

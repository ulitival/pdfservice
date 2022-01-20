"""
The module with a base representation of a CLI command
"""
from __future__ import annotations
from typing import List, Union
from abc import ABC, abstractmethod
import argparse

from . import log


class Command(ABC):
    """
    CLI semi-abstract command
    """

    Options = Union[argparse.Namespace]

    description = "OVERLOAD THIS BY THE ACTUAL COMMAND SHORT DESCRIPTION"

    def __init__(self, argv: List[str]):
        """
        :param argv: Command line arguments
        """
        self.name = argv[1]
        self.opt_parser = argparse.ArgumentParser(
            ' '.join(argv[:2]),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.argv = argv[2:]

    def option(self, *args, **kwargs) -> None:
        """
        Add command option
        Descendants (i.e. command implementations) are expected to call
        this member function in the constructor in order to register
        their specific options (parameters are simply passed to
        argparse.ArgumentParser.add_argument).
        "param args": add_argument() positional arguments
        "param kwargs": add_argument() keyword arguments
        """
        self.opt_parser.add_argument(*args, **kwargs)

    @abstractmethod
    def run(self, options: Command.Options) -> int:
        """
        Run command (implemented by the descendants)
        :param options: Command line options
        :return: Exit code
        """

    def execute(self) -> int:
        """
        Execute command (called from the CLI script)
        Parses options and calls implementation's run member function.
        :return: Exit code (from run)
        """
        log.info(f"Executing command {self.name}")
        exit_code = self.run(self.opt_parser.parse_args(self.argv))

        if exit_code == 0:
            log.info(f"Command {self.name} execution finished successfully")
        else:
            log.error(f"Command {self.name} failed with exit code {exit_code}")

        return exit_code

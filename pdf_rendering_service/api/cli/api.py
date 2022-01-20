"""
The module contains the command line specifications for invoking an application server
"""
from os import execvp
from typing import List

from pdf_rendering_service.cli import Command, log


class Gunicorn(Command):
    """
    Start PDF rendering service application server
    Note that the run implementation doesn't return. The (Python) process
    is replaced by the application server process.
    """
    description = "Start pdfservice rest api server"

    def __init__(self, argv: List[str]) -> None:
        """
        :param argv: command line argument
        """
        super().__init__(argv)
        self.option(
            "--workers", type=int, default=4,
            help="Number of application server worker processes"
        )
        self.option(
            "--host", type=str, default="127.0.0.1",
            help="Application server host (listen address)")
        self.option(
            "--port", type=int, default=3031,
            help="Application server listen port")
        self.option(
            "--timeout", type=int, default=60,
            help="Default timeout for incoming requests")

    def run(self, options: Command.Options) -> int:
        log.info(f"Starting API application server with options {options}")
        argv = [
            "Pdfservice-API-server",
            "--workers", str(options.workers),
            "--bind", f"{options.host}:{options.port}",
            "--timeout", str(options.timeout),
            "pdf_rendering_service.api.application:app",
        ]

        execvp("gunicorn", argv)

        return 0  # unreachable

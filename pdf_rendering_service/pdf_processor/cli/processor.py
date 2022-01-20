"""
The module contains the command line specifications for invoking a pdf processor worker
"""
from os import execvp
from typing import List

from pdf_rendering_service.cli import Command, log


class PdfProcessor(Command):
    """
    Start PDF worker processor.
    Note that the run implementation doesn't return. The (Python) process
    is replaced by the application server process.
    """
    description = "A worker that processes pdf documents"

    def __init__(self, argv: List[str]):
        """
        :param argv: command line arguments
        """
        super().__init__(argv)
        self.option(
            "--processes", type=int, default=4,
            help="Number of processes to spawn"
        )
        self.option(
            "--threads", type=int, default=4,
            help="Number of threads to create"
        )

    def run(self, options: Command.Options) -> int:
        log.info(f"Starting pdf worker with options {options}")
        argv = [
            "Pdfservice-pdf-processor",
            "--processes", str(options.processes),
            "--threads", str(options.threads),
            "pdf_rendering_service.pdf_processor.processor",
        ]

        execvp("dramatiq", argv)

        return 0  # unreachable

"""
The helper module for additional pdf processing, i.e. retrieving page numbers
"""
import io
import os
import pathlib

import pdfplumber
from pdfminer.pdfparser import PDFException

from pdf_rendering_service.base import log


class PdfProcessorException(Exception):
    """
    PDF files processing error
    """


class ReadingSecretsException(Exception):
    """
    Reading secrets files error, i.e. file is missing
    """


def get_pdf_page_number(pdf_content: bytes) -> int:
    """
    The helper method that gets total number of pdf pages
    :param pdf_content: a content of a pdf file as array of bytes
    :return: total number of pages in the pdf
    """
    pdf_handler = io.BytesIO(pdf_content)
    try:
        with pdfplumber.open(pdf_handler) as pdf_file:
            return len(pdf_file.pages)
    except PDFException as ex:
        log.error("Unable to retrieve number of pages from PDF")
        raise PdfProcessorException(f"Exception message: {ex}")


def read_secret(env_variable_name: str) -> str:
    """
    Reads a secret from a file with path provided in an environment variable
    :param env_variable_name: a name of a variable where a secret is stored
    :return: a secret
    """
    try:
        return pathlib.Path(os.getenv(env_variable_name)).read_text(encoding="UTF-8")
    except FileNotFoundError as ex:
        log.error(f"Unable to read a secret stored defined by {env_variable_name}")
        raise ReadingSecretsException(f"Exception message: {ex}")

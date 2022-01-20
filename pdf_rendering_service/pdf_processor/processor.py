"""
The module contains the main worker/actor for dramatiq. That actor receives a content of pdf,
creates images for every page and then stores it in the DB
"""
import io
from typing import Tuple
from uuid import UUID

import dramatiq
import pdfplumber
from pdfminer.pdfparser import PDFException
from pdfplumber.page import Page

from pdf_rendering_service.base import (
    convert_to_img_bytes,
    PdfProcessorException,
    get_converter_options
)
from pdf_rendering_service.pdf_processor import log
from pdf_rendering_service.persistence import (
    store_document_pages,
    start_processing,
    finish_processing,
    failed_processing,
)


def _prepare_page(page: Page) -> Tuple[int, bytes]:
    """
    Creates a tuple of page number and page content for a generator
    :param page: a page from a document
    :return: pair of page number and page content
    """
    new_size = (get_converter_options().get("width"), get_converter_options().get("height"))
    return page.page_number, \
           convert_to_img_bytes(
               page,
               resolution=get_converter_options().get("resolution"),
               new_size=new_size
           )


@dramatiq.actor
def process_pdf(doc_id: str, pdf_content: str) -> None:
    """
    The function serves as an dramatiq actor and performs document's pages normalization
    :param doc_id: the id of a document that is being processed
    :param pdf_content: the content of a document as a byte array
    """
    doc_id = UUID(doc_id)
    pdf_content = pdf_content.encode("Latin-1")
    start_processing(doc_id)
    pdf_handler = io.BytesIO(pdf_content)
    try:
        with pdfplumber.open(pdf_handler) as pdf_file:
            pdf_pages_gen = (_prepare_page(page) for page in pdf_file.pages)
            store_document_pages(doc_id, pdf_pages_gen)
    except PDFException as ex:
        log.error(f"PDF document {doc_id} was not processed")
        failed_processing(doc_id)
        raise PdfProcessorException(f"Exception message: {ex}")
    finish_processing(doc_id)

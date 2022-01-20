"""
The module aggregates all the necessary methods in order to communicate with a database
"""
from datetime import datetime
from typing import Dict, Union, Generator, Tuple
from uuid import UUID

from pony import orm
from pony.orm.core import OrmError, ObjectNotFound

from pdf_rendering_service.persistence import Status, Document, Page, log


class DbEngineException(Exception):
    """
    Exception class for all database related errors
    """


@orm.db_session
def store_document(num_pages: int) -> UUID:
    """
    Create a new record in a db given number of pages in pdf
    :param num_pages: number of pages in a provided pdf
    :return: document id for further processing
    """
    pending_status = Status.get(name="pending")
    new_doc = Document(status=pending_status, num_pages=num_pages,
                       creation_time=datetime.utcnow())
    return new_doc.id


@orm.db_session
def get_document_info(doc_id: UUID) -> Dict[str, Union[str, int]]:
    """
    Retrieves information about a processing document
    :param doc_id: document id for
    :return: a dictionary with information about the document status
    """
    try:
        doc = Document[doc_id]
        return {
            "status": doc.status.name,
            "n_pages": doc.num_pages
        }
    except ObjectNotFound as ex:
        log.error(f"The document with id {doc_id} wasn't found.")
        raise DbEngineException(f"Exception message: {ex}")


@orm.db_session
def get_page(doc_id: UUID, page_number: int) -> bytes:
    """
    Retrieves a page from the DB as an array of bytes that represents a PNG image
    :param doc_id: an id of a document with the requested page
    :param page_number: a requested page number
    :return: an array of bytes as a representation of a page
    """
    try:
        doc = Document[doc_id]
        return doc.get_page_by_page_number(page_number)
    except OrmError as ex:
        log.error(f"The page {page_number} in the document with id {doc_id} wasn't retrieved.")
        raise DbEngineException(f"Exception message: {ex}")


def _store_page(doc_id: UUID, page_number: int, page_img_content: bytes) -> None:
    """
    Creates a page record in the db's Page table
    :param doc_id: an id of document a page is being taken from
    :param page_number: current page's number
    :param page_img_content: image representation of a page
    """
    Page(page_number=page_number, page=page_img_content, document=doc_id)


@orm.db_session
def store_document_pages(doc_id: UUID, pages: Generator[Tuple[int, bytes], None, None]) -> None:
    """
    Stores a pdf document page as a png image (ib byte array representation) in the DB
    :param doc_id: a document id the pages are stored from
    :param pages: a generator that returns a tuple (page number, page content)
    """
    for page_number, page_content in pages:
        _store_page(doc_id, page_number, page_content)


@orm.db_session
def start_processing(doc_id: UUID) -> None:
    """
    Change the status of a document with the doc_id in Document table to `processing`
    :param doc_id: a document id for which the processing was started
    """
    doc = Document[doc_id]
    doc.set(status=Status.get(name="processing"), processing_start_time=datetime.utcnow())


@orm.db_session
def finish_processing(doc_id: UUID) -> None:
    """
    Change the status of a document with the doc_id in Document table to `done`
    :param doc_id: a document id for which the processing was successfully finished
    """
    doc = Document[doc_id]
    doc.set(status=Status.get(name="done"), processing_finished_time=datetime.utcnow())


@orm.db_session
def failed_processing(doc_id: UUID) -> None:
    """
    Change the status of a document with the doc_id in Document table to `failed`
    :param doc_id: a document id for which the processing was failed
    """
    doc = Document[doc_id]
    doc.set(status=Status.get(name="failed"), processing_finished_time=datetime.utcnow())

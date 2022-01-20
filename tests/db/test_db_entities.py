import pathlib
from datetime import datetime
from uuid import UUID

import pytest
from pony import orm


@pytest.fixture(autouse=True)
def rollback_session():
    with orm.db_session:
        yield
        orm.rollback()


def test_create_doc():
    from pdf_rendering_service.persistence import Status, Document
    processing = Status.get(name="processing")
    Document(status=processing, num_pages=5, creation_time=datetime.utcnow())
    num_of_doc = orm.select(doc for doc in Document).count()
    assert num_of_doc == 1


def test_store_document():
    from pdf_rendering_service.persistence import store_document, Document
    doc_id = store_document(num_pages=1)
    num_of_doc = orm.select(doc for doc in Document).count()
    assert num_of_doc == 1
    assert isinstance(doc_id, UUID)


def test_get_document_info():
    from pdf_rendering_service.persistence import Document, store_document, get_document_info
    doc_id = store_document(num_pages=5)
    doc_info = get_document_info(doc_id)
    num_of_docs = orm.select(doc for doc in Document).count()
    assert num_of_docs == 1
    assert doc_info.get("status") == "pending"
    assert doc_info.get("n_pages") == 5


def test_store_pages():
    from pdf_rendering_service.persistence import Document, Page, store_document_pages, \
        store_document

    pdf_file_content = pathlib.Path(__file__).parent.joinpath("../test_data/valid.pdf").read_bytes()
    doc_id = store_document(num_pages=1)
    num_of_docs = orm.select(doc for doc in Document).count()
    assert num_of_docs == 1
    store_document_pages(doc_id, ((1, pdf_file_content) for _ in range(1)))
    num_of_pages = orm.select(page for page in Page).count()
    assert num_of_pages == 1


def test_get_page_content():
    from pdf_rendering_service.persistence import Document, Page, store_document_pages, \
        store_document, get_page, DbEngineException

    pdf_file_content = pathlib.Path(__file__).parent.joinpath("../test_data/valid.pdf").read_bytes()
    doc_id = store_document(num_pages=5)
    num_of_docs = orm.select(doc for doc in Document).count()
    assert num_of_docs == 1

    store_document_pages(doc_id, ((page_num, pdf_file_content) for page_num in range(1, 6, 1)))
    num_of_pages = orm.select(page for page in Page).count()
    assert num_of_pages == 5

    page_content_from_db = get_page(doc_id, page_number=3)
    assert page_content_from_db == pdf_file_content

    # let's try to get page that is out of bound
    with pytest.raises(DbEngineException):
        _ = get_page(doc_id, page_number=6)


# TODO: The rest of the db operations will be tested in a similar way

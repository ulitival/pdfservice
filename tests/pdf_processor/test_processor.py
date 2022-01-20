import io
import pathlib

import PIL.Image as Image
from pony import orm


def test_process_pdf_successful():
    from pdf_rendering_service.pdf_processor.processor import process_pdf
    from pdf_rendering_service.persistence import Document, Page, get_page, store_document

    pdf_file_content = pathlib.Path(__file__).parent.joinpath("../test_data/valid.pdf").read_bytes()
    with orm.db_session:
        doc_id = store_document(num_pages=1)
        num_of_docs = orm.select(doc for doc in Document).count()
        process_pdf(str(doc_id), pdf_file_content.decode("Latin-1"))
        page_content = get_page(doc_id, 1)
        num_of_pages = orm.select(page for page in Page).count()
        orm.rollback()
    assert num_of_docs == 1
    assert num_of_pages == 1
    img = Image.open(io.BytesIO(page_content))
    assert img.size == (1200, 1600)
    assert img.format.lower() == "png"


# TODO: The exception handling will be tested in a similar way

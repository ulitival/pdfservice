"""
The module contains of all the necessary entities, e.g. Status, Document, Page
"""
from datetime import datetime
from uuid import UUID, uuid4

from pony import orm
from pony.orm.core import RowNotFound

from pdf_rendering_service.base import get_db_creation_options
from pdf_rendering_service.persistence import log, db


class Document(db.Entity):
    """
    The representation of the Document table
    """
    id = orm.PrimaryKey(UUID, auto=True, default=uuid4)
    status = orm.Required(lambda: Status, column="status_id")
    num_pages = orm.Required(int)
    pages = orm.Set(lambda: Page)
    creation_time = orm.Required(datetime)
    processing_start_time = orm.Optional(datetime)
    processing_finished_time = orm.Optional(datetime)

    def get_page_by_page_number(self, page_number: int) -> bytes:
        """
        The query finds a specific page within all the pages of a document
        :param page_number: a requested page number
        :return: a page from the DB
        """
        res = self.pages.select(lambda page: page.page_number == page_number).first()
        if res is None:
            log.error(f"The page: {page_number} was not found for the document id {self.id}")
            raise RowNotFound("The requested page was not found in the document")
        return res.page


class Status(db.Entity):
    """
    The representation of the Status table
    """
    name = orm.Required(str, unique=True)
    documents = orm.Set(Document, cascade_delete=False)


class Page(db.Entity):
    """
    The representation of the Page table
    """
    page_number = orm.Required(int, column="p_number")
    page = orm.Required(bytes)
    document = orm.Required(Document, column="document_id")


db.generate_mapping(create_tables=get_db_creation_options().get("create_tables", False))

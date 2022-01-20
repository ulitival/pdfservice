"""
The package represents persistence layer. All the data models are stored under this package.
The `persistence` package also provides a singleton of db communication class.
"""
from pony import orm

from pdf_rendering_service.base import get_logger, get_db_connection_options

log = get_logger("pdfservice.persistence")

db = orm.Database()
db.bind(**get_db_connection_options())

from .entities import (
    Document,
    Status,
    Page
)
from .engine import (
    store_document,
    get_document_info,
    get_page,
    store_document_pages,
    start_processing,
    finish_processing,
    failed_processing,
    DbEngineException
)

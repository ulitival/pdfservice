"""
The module consists of different configurations related either to the persistence or processor
package. Having configuration in a separate module helps to mock it in tests.
"""
import os

from pdf_rendering_service.base import read_secret


def get_db_connection_options():
    """
    Returns configuration options for database connection
    """
    return {
        "provider": "postgres",
        "user": read_secret("POSTGRES_USER_NAME_FILE"),
        "password": read_secret("POSTGRES_PASSWORD_FILE"),
        "host": os.getenv("POSTGRES_HOST"),
        "database": read_secret("POSTGRES_DB_FILE")
    }


def get_db_creation_options():
    """
    Returns configuration options for database creation. Used primarily for testing
    """
    return {
        "create_tables": False
    }


def get_converter_options():
    """
    Returns configuration options for pdf to image conversion
    """
    return {
        "width": os.getenv("PDFSERVICE_NORM_WIDTH", 1200),
        "height": os.getenv("PDFSERVICE_NORM_HEIGHT", 1600),
        "resolution": os.getenv("PDFSERVICE_IMAGE_RESOLUTION", 150)
    }

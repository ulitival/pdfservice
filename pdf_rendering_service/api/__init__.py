"""
API related things goes to this package, that includes defining routes/endpoints, main Flask
entrypoint and others
"""
from pdf_rendering_service.base import get_logger
log = get_logger("pdfservice.api")

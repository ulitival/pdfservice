"""
The module contains endpoints for the API version 1
"""

import mimetypes
from http import HTTPStatus
from json import dumps as jsonify
from uuid import UUID

from flask import request as req, Blueprint, Response
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from pdf_rendering_service.api import log
from pdf_rendering_service.api.common import resp
from pdf_rendering_service.base import get_pdf_page_number, PdfProcessorException
from pdf_rendering_service.pdf_processor.processor import process_pdf
from pdf_rendering_service.persistence import store_document, get_document_info, \
    get_page, DbEngineException

api: Blueprint = Blueprint("v1", __name__)


@api.route("/documents", methods=["POST"])
def documents():
    """
    The endpoint accepts a PDF file for preparing it for rendering.
    :return: a document id
    """
    if "file" not in req.files:
        log.warning("A file was not uploaded")
        raise BadRequest(description="File was not provided.")
    file_content_type = req.files.get("file").content_type
    if file_content_type != mimetypes.types_map.get(".pdf"):
        log.warning(
            f"A different type of a document was uploaded. Got the mimetype {file_content_type}")
        raise BadRequest(description="The uploaded file is not of type pdf.")

    file_content = req.files.get("file").read()
    try:
        num_pages = get_pdf_page_number(file_content)
    except PdfProcessorException as ex:
        log.error("An error happened during initial pdf processing.")
        raise InternalServerError(f"A provided pdf is invalid. {ex}")
    doc_id_uuid_str = str(store_document(num_pages=num_pages))
    process_pdf.send(doc_id_uuid_str, file_content.decode("Latin-1"))
    return resp(jsonify({"id": doc_id_uuid_str}), status=HTTPStatus.CREATED)


@api.route("/documents/<uuid:document_id>", methods=["GET"])
def get_document(document_id: UUID) -> Response:
    """
    The endpoint returns information about a document with `document_id`. The information includes
    current status of the document ("processing", "done", "failed") and the total number of pages.
    :param document_id: an id of a requested document
    :return: current status of processing and the total number of pages for a document.
    """
    try:
        return resp(jsonify(get_document_info(document_id)), status=HTTPStatus.OK)
    except DbEngineException as ex:
        log.error(f"A document with id {document_id} was not found")
        raise NotFound(f"A requested document was not retrieved. {ex}")


@api.route("/documents/<uuid:document_id>/pages/<int:page_number>", methods=["GET"])
def get_document_page(document_id: UUID, page_number: int) -> Response:
    """
    The endpoint returns a normalized page, i.e. the page as a png image with dimension of
    1200 x 1600 pixels.
    :param document_id: an id of a document where a requested page is located
    :param page_number: a page number in the document
    :return: a page from a document as a png image
    """
    # TODO: Check total number of pages here
    # TODO: Check if document was successfully processed before returning a page
    try:
        page = get_page(document_id, page_number)
    except DbEngineException as ex:
        log.error(f"A page {page_number} from a document with id {document_id} was not found")
        raise NotFound(f"A requested page was not retrieved. {ex}")
    return resp(page, status=HTTPStatus.OK, mimetype=mimetypes.types_map.get(".png"))

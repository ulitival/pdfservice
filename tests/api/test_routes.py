import io
import pathlib
from http import HTTPStatus
from typing import Tuple
from uuid import uuid4, UUID

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockerFixture


@pytest.fixture
def mock_db(mocker: MockerFixture) -> None:
    # we can safely mock here imported functions as a part of `.api.v1.routes` and
    # `.pdf_processor.processor` namespaces because the first import happened at the time
    # when Flask test client was created and now those function belongs to the namespaces where
    # they were imported
    mocker.patch(
        "pdf_rendering_service.api.v1.routes.store_document",
        new=lambda *args, **kwargs: uuid4()
    )
    mocker.patch(
        "pdf_rendering_service.pdf_processor.processor.store_document_pages",
        new=lambda *args, **kwargs: None
    )


def is_valid_uuid(uuid_candidate: str, version: int) -> bool:
    try:
        UUID(uuid_candidate, version=version)
    except ValueError:
        return False
    return True


def get_file_content_and_name(path: str) -> Tuple[io.BytesIO, str]:
    file_path = pathlib.Path(__file__).parent.joinpath(path)
    return io.BytesIO(file_path.read_bytes()), file_path.name


def test_documents_endpoint_without_file(client: FlaskClient) -> None:
    resp_body = client.post('/documents').json
    assert resp_body.get("code") == HTTPStatus.BAD_REQUEST
    assert resp_body.get("name").lower() == HTTPStatus.BAD_REQUEST.phrase.lower()
    assert resp_body.get("description") == "File was not provided."


def test_documents_endpoint_invalid_pdf_file(client: FlaskClient) -> None:
    resp_body = client.post(
        '/documents',
        data={
            "file": get_file_content_and_name("../test_data/invalid.pdf")
        }
    ).json
    assert resp_body.get("code") == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_body.get("name").lower() == HTTPStatus.INTERNAL_SERVER_ERROR.phrase.lower()
    assert resp_body.get(
        "description") == "A provided pdf is invalid. Exception message: No /Root object! - Is this really a PDF?"


def test_documents_endpoint_not_a_pdf_file(client: FlaskClient) -> None:
    resp_body = client.post(
        '/documents',
        data={
            "file": get_file_content_and_name("../test_data/not_a_pdf.txt")
        }
    ).json
    assert resp_body.get("code") == HTTPStatus.BAD_REQUEST
    assert resp_body.get("name").lower() == HTTPStatus.BAD_REQUEST.phrase.lower()
    assert resp_body.get("description") == "The uploaded file is not of type pdf."


def test_documents_endpoint_valid_pdf_file(client: FlaskClient, mock_db) -> None:
    resp = client.post(
        '/documents',
        data={
            "file": get_file_content_and_name("../test_data/valid.pdf")
        }
    )
    assert resp.status_code == HTTPStatus.CREATED
    resp_body = resp.json
    assert "id" in resp_body
    assert is_valid_uuid(resp_body.get("id"), version=4)


# TODO: The rest of the endpoints will be tested in a similar way

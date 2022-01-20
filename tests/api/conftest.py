from typing import Generator

import pytest
from flask.testing import FlaskClient


@pytest.fixture(scope="package")
def client() -> Generator[FlaskClient, None, None]:
    from pdf_rendering_service.api.application import app
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client

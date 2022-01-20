import pytest
from dramatiq.brokers.stub import StubBroker
from pony import orm
from pytest_mock import MockerFixture


@pytest.fixture(scope="session", autouse=True)
def mock_read_secrets(session_mocker: MockerFixture) -> None:
    session_mocker.patch("pdf_rendering_service.base.read_secret",
                         new=lambda *args, **kwargs: "psst, it's a secret")


@pytest.fixture(scope="session", autouse=True)
def mock_broker(session_mocker: MockerFixture) -> None:
    session_mocker.patch("dramatiq.brokers.rabbitmq.RabbitmqBroker",
                         new=lambda *args, **kwargs: StubBroker())


@pytest.fixture(scope="session", autouse=True)
def mock_db_options(session_mocker: MockerFixture, mock_read_secrets) -> None:
    in_memory_db_options = {
        "provider": "sqlite",
        "filename": ":memory:"
    }
    session_mocker.patch("pdf_rendering_service.base.get_db_connection_options",
                         new=lambda: in_memory_db_options)

    session_mocker.patch("pdf_rendering_service.base.get_db_creation_options",
                         new=lambda: {"create_tables": True})

    from pdf_rendering_service.persistence import Status
    with orm.db_session:
        Status(name="processing")
        Status(name="done")
        Status(name="failed")
        Status(name="pending")

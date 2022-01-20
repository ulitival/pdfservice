"""
The package represents a pdf worker that will run inside dramatiq environment. It as well
contains additional helpers for processing pdfs
"""
import os

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

from pdf_rendering_service.base import get_logger, read_secret

log = get_logger("pdfservice.pdf_processor")

rabbitmq_user = read_secret("RABBITMQ_DEFAULT_USER_FILE")
rabbitmq_passwd = read_secret("RABBITMQ_DEFAULT_PASS_FILE")
rabbitmq_host = os.getenv("RABBITMQ_HOST")
rabbitmq_port = os.getenv("RABBITMQ_PORT")
rabbitmq_connection = f"amqp://{rabbitmq_user}:{rabbitmq_passwd}@{rabbitmq_host}:{rabbitmq_port}"

broker = RabbitmqBroker(url=rabbitmq_connection)
dramatiq.set_broker(broker)

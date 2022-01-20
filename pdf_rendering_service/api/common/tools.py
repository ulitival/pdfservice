"""
This module contains different helpers related to the API package
"""

from http import HTTPStatus
from typing import Union

from flask import Response


def resp(
        content: Union[str, bytes],
        status: int = HTTPStatus.OK,
        mimetype: str = "application/json"):
    """
    Produce response
    :param mimetype: A mime type of a returned content
    :param content: Response body (direct content or content chunks generator)
    :param status: Response status
    :return: JSON content type response object
    """
    return Response(content, status=status, mimetype=mimetype)

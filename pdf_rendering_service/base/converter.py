"""
This helper module contains functions related to any conversion
"""
from io import BytesIO
from typing import Optional, Tuple

import PIL
from pdfplumber.page import Page


def convert_to_img_bytes(page: Page, resolution: int = 150,
                         new_size: Optional[Tuple[int, int]] = None,
                         img_format: str = "png") -> bytes:
    """
    The function converts a document's page represented by `pdfplumber.page.Page` to a byte array
    :param page: a document's page
    :param resolution: a desired resolution of an image
    :param new_size: a new desired size
    :param img_format: a format of an output image
    :return: a byte array representing an image
    """
    img = page.to_image(resolution=resolution)
    if new_size is not None:
        img.original = img.original.resize(new_size)
    temp_img = PIL.Image.new(img.original.mode, img.original.size)
    temp_img.paste(img.original)
    img_content = BytesIO()
    temp_img.save(img_content, img_format)
    return img_content.getvalue()

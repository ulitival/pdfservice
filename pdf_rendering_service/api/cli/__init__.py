"""
The package with declared api cli commands
"""
from .api import Gunicorn

options = {
    "api": Gunicorn
}

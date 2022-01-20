"""
The module defines the API main entrypoint
"""

import mimetypes
from json import dumps as jsonify

from flask import Flask
from pony.flask import Pony
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from .v1 import api as api_v1


app = Flask(__name__)
app.register_blueprint(api_v1, url_prefix="/v1")

# Default (latest stable) API contract version
app.register_blueprint(api_v1, name="latest")
# Let's wrap our Flask app into Pony wrapper so we have db_session for every route
Pony(app)


# define an universal error handling
@app.errorhandler(HTTPException)
def error_handler(ex: HTTPException) -> Response:
    """Return JSON instead of HTML for HTTP errors."""
    response = ex.get_response()
    response.data = jsonify(indent=4, sort_keys=True, obj={
        "code": ex.code,
        "name": ex.name,
        "description": ex.description
    })

    response.content_type = mimetypes.types_map.get(".json")
    return response

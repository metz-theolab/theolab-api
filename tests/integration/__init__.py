"""Create TestClient for integration tests of the API.
"""

from fastapi.testclient import TestClient
from backend.api.app import create_app


# TODO: here database settings should be configured for custom environment of integration tests.


app = create_app()


test_client = TestClient(app)


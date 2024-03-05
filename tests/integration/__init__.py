"""Create TestClient for integration tests of the API.
"""

from fastapi.testclient import TestClient
from backend.api.app import create_app, AppSettings, OIDCSettings


# TODO: here database settings should be configured for custom environment of integration tests.

TEST_SETTINGS = AppSettings(
    oidc = OIDCSettings(enabled=False)
)


app = create_app(settings=TEST_SETTINGS)


test_client = TestClient(app)

# Environment
DB_URI = "mysql://root:root@localhost:3306"
DB_NAME = "QD"
SCRIBES_DB = "scribes"
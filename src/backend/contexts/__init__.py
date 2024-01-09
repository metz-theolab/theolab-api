from fastapi import Request
from .manuscripts.router import router as manuscript_router
from .text.router import router as text_router
from .manuscripts.db import ManuscriptClient

ROUTERS = [manuscript_router, text_router]


class APISQLClient(ManuscriptClient):
    """Create MixIn of all databases.
    """

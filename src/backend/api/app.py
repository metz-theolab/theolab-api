"""Define app.
"""
import contextlib
import typing as t

from fastapi import FastAPI
from pydantic_settings import BaseSettings

from ..contexts import ROUTERS, APISQLClient, scribes_router


class OIDCSettings(BaseSettings):
    enabled: bool = True
    issuer_url: str = "http://localhost:8024"
    realm: str = "theolab"
    client_id: str = "qwb-api"
    retry: bool = True
    max_attempts: int = 5


class AppSettings(BaseSettings):
    oidc: OIDCSettings = OIDCSettings()
    database_uri: str = "mysql://root:root@localhost:3306"
    database_name: str = "QD"


def create_app(settings: t.Optional[AppSettings] = None,
               scribes: bool = False) -> FastAPI:
    """This is the application factory, e.g., a function responsible for
    creating a fresh new instance of application.
    """
    # Parse application settings
    settings = settings or AppSettings()

    # If SCRIBES only mode is set, set scribes to True
    if scribes:
        settings.database_name = "scribes"
        settings.database_uri = "postgresql://root:root@localhost:5432"
    # Create database client according to application settings
    db = APISQLClient(
        settings.database_uri, settings.database_name
    )


    # Define application lifespan
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        await db.connect()
        yield

    # Create fastapi instance
    app = FastAPI(lifespan=lifespan)

    # Attach settings to application
    app.state.settings = settings

    # Attach db to app state
    app.state.database = db

    # Set up the keycloak OIDC client
    from .oidc.provider import oidc_provider
    oidc_provider(app)

    if scribes:
        # If scribes only mode is activated, only make
        # available scribes related endpoints
        app.include_router(scribes_router)
    else:
        # Include routers
        for router in ROUTERS:
            app.include_router(router)

    # Return new application instance
    return app


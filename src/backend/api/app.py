"""Define app.
"""
import contextlib
import typing as t

from fastapi import FastAPI
from pydantic_settings import BaseSettings


from ..contexts import ROUTERS, APISQLClient



class AppSettings(BaseSettings):
    database_uri: str = "mysql://root:root@localhost:3306"
    database_name: str = "QD"


def create_app(settings: t.Optional[AppSettings] = None) -> FastAPI:
    """This is the application factory, e.g., a function responsible for
    creating a fresh new instance of application.
    """
    # Parse application settings
    settings = settings or AppSettings()

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

    # Include routers
    for router in ROUTERS:
        print("including router")
        app.include_router(router)

    # Return new application instance
    return app

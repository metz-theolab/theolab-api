import uvicorn

from backend.api.app import create_app
from backend.settings.settings import APISettings


def main():
    # TODO: parse settings from YAML files
    api_settings = APISettings()
    uvicorn.run(
        port=api_settings.port,
        host=api_settings.host,
        factory=True,
        app=create_app,
    )


if __name__ == "__main__":
    main()

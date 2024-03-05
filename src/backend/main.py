from functools import partial
import uvicorn
import click

from backend.api.app import create_app
from backend.settings.settings import APISettings


@click.command()
@click.option('--scribes-only',
              default=False,
              is_flag=True,
              help='Only activate endpoints related to scribes')
def main(scribes_only: bool):
    # TODO: parse settings from YAML files
    api_settings = APISettings()
    uvicorn.run(
        port=api_settings.port,
        host=api_settings.host,
        factory=True,
        app=partial(create_app, scribes=scribes_only),
    )


if __name__ == "__main__":
    main()

from functools import partial
from pathlib import Path
import uvicorn
import click
import yaml

from backend.api.app import create_app
from backend.settings.settings import APISettings


@click.command()
@click.option('--scribes-only',
              default=False,
              is_flag=True,
              help='Only activate endpoints related to scribes')
@click.option('--port',
              type=int,
              metavar="NUMBER",
              default=None,
              help='Port to run the API on')
@click.option('--host',
              type=str,
              metavar="ADDRESS",
              default=None,
              help='Host to run the API on')
@click.option('--config',
              type=str,
              metavar="PATH",
                default=None,
                help='Path to config file')
def main(
    scribes_only: bool,
    port: int,
    host: str,
    config: str,
):
    raw_settings = dict()
    if config is not None:
        config_filepath = Path(config).expanduser().resolve(True)
        config_content = yaml.safe_load(config_filepath.read_text())
        raw_settings.update(config_content)
    if port is not None:
        raw_settings["port"] = port
    if host is not None:
        raw_settings["host"] = host
    api_settings = APISettings(**raw_settings)
    uvicorn.run(
        port=api_settings.port,
        host=api_settings.host,
        factory=True,
        app=partial(create_app, scribes=scribes_only),
    )


if __name__ == "__main__":
    main()

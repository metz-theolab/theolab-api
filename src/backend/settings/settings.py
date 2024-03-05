"""Settings for lauching the API.
"""
from pydantic_settings import BaseSettings



class APISettings(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"


QWB_CLIENT_ID = "qwb-api"
QWB_READ_ROLE = "read"

#TODO: create scribes specific client id
SCRIBES_CLIENT_ID = "qwb-api"
SCRIBES_READ_ROLE = "read"
"""Settings for lauching the API.
"""
from pydantic_settings import BaseSettings



class APISettings(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"

"""Set of utility functions for the API.
"""
from typing import Union


def format_readings_output(readings: list[dict[str, str]]) -> str:
    """Format readings output to be returned to the client.
    """
    print(readings)
    return "\n".join([reading['content'] for reading in readings])
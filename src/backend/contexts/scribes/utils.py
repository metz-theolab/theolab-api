"""Set of utility functions for the API.
"""
from typing import Any


def format_readings_output(readings: dict[str, dict[str, str]]) -> list[Any]:
    """Format readings output to be returned to the client.
    """
    readings_output = []
    for column, column_content in readings.items():
        column_readings = {}
        column_readings["column"] = column
        for _, line_content in column_content.items():
            try:
                column_readings["content"] += line_content + "\n"
            except KeyError:
                column_readings["content"] = line_content + "\n"
        readings_output.append(column_readings)
    return readings_output


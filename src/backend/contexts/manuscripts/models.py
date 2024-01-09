"""Data model for manuscript data retrieval manipulation.
"""
from enum import Enum

FOLLOWED_BY_MAPPER = {
    "space": " ",
    "break": "\n",
    "none": "",
}

class ManuscriptAttributes(str, Enum):
    """Attributes of a manuscript.
    """
    column = "column"
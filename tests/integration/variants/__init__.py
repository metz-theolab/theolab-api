"""Unit tests for the variants module.
"""

from backend.contexts.collations.utils import *
from textdistance import levenshtein

def compute_levensthein(reading_1, reading_2):
    """Compute the levensthein distance between two readings.
    """
    return levenshtein(reading_1, reading_2)


def compute_letter_differences(reading_1: str, reading_2: str):
    """Return the list of letters that are different between two readings.
    """
    return set(reading_1 + reading_2)


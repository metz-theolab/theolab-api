"""Set of utility functions for variant analysis.
"""
import re
from textdistance import levenshtein
from collatex.core_classes import AlignmentTable


def compute_levensthein(reading_1, reading_2):
    """Compute the levensthein distance between two strings."""
    return levenshtein(reading_1, reading_2)


def compute_letter_difference(reading_1, reading_2):
    """Return the set of distinct letters between two strings."""
    return list((set(reading_1) - set(reading_2)) | (set(reading_2) - set(reading_1)))


def retrieve_morphological_analysis(reading_info):
    """Retrieve all possibles morphological analysis of a reading."""
    morphological_analysis = []
    for info in reading_info:
        morphological_analysis.append(info["morphological_analysis"])
    # Return unique morphological analysis
    return [dict(s) for s in set(frozenset(d.items()) for d in morphological_analysis)]


def detect_omission(variant_list: list[str]):
    """Detect an omission."""
    return "" in variant_list


def analyze_variants(variant_list: list[str]):
    """Given a list of variants, perform the analysis."""
    return {
        "guessed_type": "omission" if detect_omission(variant_list) else "unknown",
        "distance": compute_levensthein(variant_list[0], variant_list[1]),
        "letter_difference": compute_letter_difference(
            variant_list[0], variant_list[1]
        ),
        "reading_1": variant_list[0],
        "reading_2": variant_list[1],
    }


def combine_values(dictionary):
    result = {}

    # Iterate through all unique key pairs in the dictionary
    for i, (key1, value1) in enumerate(dictionary.items()):
        for key2, value2 in list(dictionary.items())[i + 1 :]:
            # Create a new key by combining the original keys
            new_key = f"{key1}-{key2}"

            # Combine the corresponding values into a new list
            new_value = value1 + value2

            # Update the result dictionary
            result[new_key] = new_value

    return result


def strip_hebrew_vowels(hebrew_string):
    """Strip vowels from Hebrew string.
    """
    # Define a regular expression to match Hebrew vowels
    vowels_pattern = re.compile('[\u05B0-\u05C3\u05C7-\u05C8\u05F0-\u05F4\u05BC\u05B0-\u05B9\u05F3-\u05F4\u0591-\u05AF]')  # Hebrew vowels unicode range

    # Use re.sub to replace matched vowels with an empty string
    stripped_string = re.sub(vowels_pattern, '', hebrew_string)

    return stripped_string


def analyze_collations(alignment_table: AlignmentTable):
    """Analyze an input collation table."""
    variant_analysis = {}
    for ix, col in enumerate(alignment_table.columns):
        if col.variant:
            variants = col.tokens_per_witness
            for key, val in variants.items():
                if val == []:
                    variants[key] = [""]
                else:
                    variants[key] = [item for item in val]   
            combined_values = combine_values(variants)
            for key, value in combined_values.items():
                string_value = [val.token_string if type(val) != str else val for val in value]
                if string_value[0] != string_value[1]:
                    variant_analysis[str(ix)+":"+key] = analyze_variants(string_value)
    return variant_analysis

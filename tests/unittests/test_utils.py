"""Tests for variant analysis.
"""
import unittest
from backend.contexts.collations.utils import compute_levensthein, compute_letter_difference, \
    retrieve_morphological_analysis, detect_omission, analyze_variants, combine_values


class TestUtils(unittest.TestCase):
    """
    Tests for variant analysis.
    """

    def test_compute_levensthein(self):
        """
        Test the levensthein distance between two strings.
        """
        self.assertEqual(compute_levensthein("reading_1", "reading_2"), 1)

    def test_compute_letter_difference(self):
        """
        Test the set of distinct letters between two strings.
        """
        self.assertCountEqual(
            compute_letter_difference("reading_1", "reading_2"), ["1", "2"]
        )

    def test_retrieve_morphological_analysis(self):
        """
        Test the retrieval of all possibles morphological analysis of a reading.
        """
        reading_info = [{'position': {'manuscript_sign_cluster_reading_id': 4073, 
                                      'manuscript': '1QS', 
                                      'column': '1', 
                                      'line': '1', 
                                      'sequence_in_line': 3}, 
                        'morphological_analysis': {'lemma': 'ל',
                                                   'word_class': 'Präposition',
                                                   'short_definition': 'zu, hin',                                                                                                                                  
                                                    'root_designation': 'II', 
                                                    'verb_stem': None, 
                                                    'verb_tense': None, 
                                                    'person': None, 
                                                    'gender': None, 
                                                    'number': None, 
                                                    'state': None, 
                                                    'augment': None, 
                                                    'suffix_person': None, 
                                                    'suffix_gender': None, 
                                                    'suffix_number': None}}]
        self.assertEqual(
            retrieve_morphological_analysis(reading_info),
            [{'augment': None,
              'gender': None,
              'lemma': 'ל',
              'number': None,
              'person': None,
              'root_designation': 'II',
              'short_definition': 'zu, hin',
              'state': None,
              'suffix_gender': None,
              'suffix_number': None,
              'suffix_person': None,
              'verb_stem': None,
              'verb_tense': None,
              'word_class': 'Präposition'}],
        )

    def test_detect_omission(self):
        """
        Test the detection of an omission.
        """
        self.assertEqual(detect_omission(["", "variant_2"]), True)

    def test_analyze_variants(self):
        """
        Test the analysis of a list of variants.
        """
        self.assertCountEqual(
            analyze_variants(["variant_1", "variant_2"]),
            {
                "guessed_type": "unknown",
                "distance": 1,
                "letter_difference": ["1", "2"],
                "reading_1": "variant_1",
                "reading_2": "variant_2",
            },
        )

    def test_combine_values(self):
        """
        Test the combination of values in a dictionary.
        """
        dictionary = {
            "key_1": ["value_1"],
            "key_2": ["value_2"],
            "key_3": ["value_3"],
        }
        self.assertEqual(
            combine_values(dictionary),
            {
                "key_1-key_2": ["value_1", "value_2"],
                "key_1-key_3": ["value_1", "value_3"],
                "key_2-key_3": ["value_2", "value_3"],
            },
        )


if __name__ == "__main__":
    unittest.main()

"""Tests that the manuscript data is properly retrieved from the database.
"""

import unittest

from .. import test_client


class TestRetrieveManuscript(unittest.TestCase):
    """Mock test of manuscript retrieval.
    """

    def test_mock(self):
        response = test_client.get("/manuscript/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"manuscript_A": "content"})
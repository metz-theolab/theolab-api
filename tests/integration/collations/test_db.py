"""Tests that the parallels are properly retrieved.
"""

import unittest
from .. import DB_URI, DB_NAME
from backend.contexts.collations.db import TextClient


class TestRetrieveManuscript(unittest.IsolatedAsyncioTestCase):
    """Mock test of manuscript retrieval.
    """
    async def asyncSetUp(self) -> None:
        self.client = TextClient(DB_URI, DB_NAME)
        await self.client.connect()

    async def test_retrieve_manuscripts(self):
        """Tests that the list of parallels is properly retrieved from the database. 
        """
        results = await self.client.get_parallels(
            name="Gen",
            chapter="1",
            verse="1"
        )
        self.assertCountEqual(
            results,
            ['Gen_SP', '4Q8b', '4Q2', '4Q7']
        )

    async def test_retrieve_parallels_contents(self):
        """Tests that the parallels are properly retrieved from the database.
        """
        results = await self.client.get_parallels_content(
            name="Gen",
            chapter="1",
            verse="1"
        )
        self.assertEqual(
            results,
            {'4Q2': 'בראשית ברא אלהי[ם את השמים ואת הארץ ', 
             '4Q7': 'בראש[ית ברא ]אלהים את השמים ואת הארץ ',
            '4Q8b': 'ברשית֯\n', 
            'Gen_SP': 'בראשית ברא אלהים את השמים ואת הארץ\n'}
        )


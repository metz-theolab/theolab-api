"""Tests that the manuscript data is properly retrieved from the database.
"""

import unittest
from .. import DB_URI, DB_NAME
from backend.contexts.manuscripts.db import ManuscriptClient

class TestRetrieveManuscript(unittest.IsolatedAsyncioTestCase):
    """Mock test of manuscript retrieval.
    """
    async def asyncSetUp(self) -> None:
        self.client = ManuscriptClient(DB_URI, DB_NAME)
        await self.client.connect()

    def test_build_manuscript_query(self):
        """Test that the manuscript query is properly built.
        """
        query = self.client.manuscript_query("4Q157")
        self.assertEqual(
            query,
            """SELECT manuscript_view.manuscript, manuscript_view.reading, manuscript_view.followed_by, manuscript_view.sequence_in_line, manuscript_view.line FROM manuscript_view WHERE manuscript_view.manuscript = '4Q157' AND manuscript_view.language_id = 1"""
        )

    def test_build_manuscript_query_column(self):
        """Test that the manuscript query is properly built with column option.
        """
        query = self.client.manuscript_query("4Q157", column="a")
        self.assertEqual(
            query,
            """SELECT manuscript_view.manuscript, manuscript_view.reading, manuscript_view.followed_by, manuscript_view.sequence_in_line, manuscript_view.line FROM manuscript_view WHERE manuscript_view.manuscript = '4Q157' AND manuscript_view.column = 'a' AND manuscript_view.language_id = 1"""
        )

    def test_build_manuscript_query_line(self):
        """Test that the manuscript query is properly built with line option.
        """
        query = self.client.manuscript_query("4Q157", column="a", line="1")
        self.assertEqual(
            query,
            """SELECT manuscript_view.manuscript, manuscript_view.reading, manuscript_view.followed_by, manuscript_view.sequence_in_line, manuscript_view.line FROM manuscript_view WHERE manuscript = '4Q157' AND manuscript_view.column = 'a' AND manuscript_view.line = '1' AND manuscript_view.language_id = 1"""
        )

    def test_build_manuscript_query_line_without_column(self):      
        """Test that the manuscript query is properly built with line option and without column option.
        """
        with self.assertRaises(ValueError):
            self.client.manuscript_query("4Q157", line="1")

    async def test_check_manuscript_exists(self):
        """Test that the manuscript existence is properly checked.
        """
        exists = await self.client.check_manuscript_exists("4Q157")
        self.assertTrue(exists)
        not_exists = await self.client.check_manuscript_exists("unknown")
        self.assertFalse(not_exists)

    async def test_get_manuscript_full(self):
        """Test that the manuscript data is properly retrieved from the database.
        """
        manuscript = await self.client.get_manuscript("4Q157")
        self.assertEqual(
            manuscript,
"[--]\n[-- עלו]הי עננא\n[-- ביו]מ֯י שנה\n[-- ]־־־\n[-- מדנ]ח\nאנ֯[כיר? --]\nהאנש מא[לה --]\nובמלאכו֯[הי --]\nד֯בעפרא [--]\nומן בלי מני[ח --]\nימותון ולא ב֯[חכ]מ֯[ה --]\nת֯בקה _____ הלא סכל יק֯[טל --]\nואנה חזי֯ת ד֯ר֯ש֯ע מ֯[ו]עה ולטת ל־[ --]\n[מפ]ר֯ק[ן?] והת־־[ ]־־־[ --]\n[-- ]ל֯[ --]\n"
)

    async def test_get_manuscript_column(self):
        """Test that the manuscript data is properly retrieved from the database with column option.
        """
        manuscript = await self.client.get_manuscript("4Q157", column="frg. 1 i")
        self.assertEqual(
            manuscript,
            "[--]\n[-- עלו]הי עננא\n[-- ביו]מ֯י שנה\n[-- ]־־־\n[-- מדנ]ח\n"
        )

    async def test_get_manuscript_line(self):
        """Test that the manuscript data is properly retrieved from the database with line option.
        """
        manuscript = await self.client.get_manuscript("4Q157", column="frg. 1 i", line="1")
        self.assertEqual(
            manuscript, "[--]\n"
        )

    async def test_build_attribute_query(self):
        """Test that the manuscript attribute query is properly built.
        """
        query = self.client.attribute_query("4Q157", "column")
        self.assertEqual(
            query,
            """SELECT DISTINCT manuscript_view.column FROM manuscript_view WHERE manuscript_view.manuscript = '4Q157'"""
        )

    async def test_get_manuscript_attribute_list(self):
        """Test that the manuscript attribute list is properly retrieved from the database.
        """
        attributes = await self.client.get_manuscript_attribute("4Q157", "column")
        self.assertEqual(attributes, ["frg. 1 i", "frg. 1 ii"])

    def test_unpack_manuscript_data(self):
        """Test that unpacking manuscript data behaves as expected.
        """
        records = [
            {"reading": "a", "followed_by": "space", "sequence_in_line": 1, "line": 1},
            {"reading": "b", "followed_by": "space", "sequence_in_line": 2, "line": 1},
            {"reading": "c", "followed_by": "space", "sequence_in_line": 3, "line": 1},
        ]
        manuscript = self.client.unpack_manuscript_data(records)
        self.assertEqual(manuscript, "a b c ")

    def test_build_distinct_manuscript_query(self):
        """Test that the distinct manuscript query is properly built.
        """
        expected_query = """SELECT DISTINCT manuscript FROM manuscript_view"""
        self.assertEqual(
            expected_query,
            self.client.distinct_manuscript_query()
        )

    async def test_retrieve_distinct_manuscripts(self):
        """Tests that the distinct manuscripts are properly retrieved from the database.
        """
        distinct_manuscripts = ["4Q157"]
        retrieved_manuscripts = await self.client.get_distinct_manuscripts()
        self.assertListEqual(
            distinct_manuscripts,
            retrieved_manuscripts
        )



if __name__ == "__main__":
    unittest.main()
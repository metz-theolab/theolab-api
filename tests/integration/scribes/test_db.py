"""Integration tests for SCRIBES database operations.
"""
from random import randint
import unittest
from .. import DB_URI, SCRIBES_DB
from backend.contexts.scribes.db import SCRIBESClient


class TestSCRIBESClient(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.client = SCRIBESClient(DB_URI, SCRIBES_DB)
        self.nbr = randint(0, 10000)
        await self.client.connect()


class TestDBInsertionDeletion(TestSCRIBESClient):
    """Test all insertions and deletions within the database.
    """

    async def asyncTearDown(self) -> None:
        await self.client.disconnect()

    async def test_add_user_tradition_success(self):
        """Test the insertion of a user tradition within the database as a success.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=False,
                                        user="test_user")
        # Check that user "test" cannot access tradition
        with self.assertRaises(ValueError):
            await self.client.fetch_tradition_id(f"Isaiah{self.nbr}",
                                                 user="test")
        # Add a new user
        await self.client.add_user_tradition(
            username="test",
            tradition=f"Isaiah{self.nbr}",
            user="test_user")
        # Check that it can access the tradition
        await self.client.fetch_tradition_id(f"Isaiah{self.nbr}",
                                             user="test")

    async def test_insert_tradition_success(self):
        """Test the insertion of a tradition within the database as a success.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        # Check that no error is raised when inserting the tradition
        tradition = await self.client.fetch_tradition_id(f"Isaiah{self.nbr}")
        try:
            self.assertIsNotNone(tradition)
        except Exception as e:
            self.fail(f"Tradition not inserted: {e}")

    async def test_insert_tradition_already_exists(self):
        """Test the failed insertion of a tradition within the database that already exists."""
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        with self.assertRaises(ValueError):
            await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                            note="Demo tradition",
                                            is_public=True,
                                            user="test_user")

    async def test_insert_manuscript(self):
        """Test the insertion of a manuscript within the database.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo manuscript",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        # Check that no error is raised when inserting the manuscript
        manuscript = await self.client.fetch_manuscript_id(manuscript=f"A{self.nbr}",
                                                           tradition=f"Isaiah{self.nbr}")
        try:
            self.assertIsNotNone(manuscript)
        except Exception as e:
            self.fail(f"Manuscript not inserted: {e}")

    async def test_insert_manuscript_already_exists(self):
        """Test the failed insertion of a manuscript within the database if it already exists.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo manuscript",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        with self.assertRaises(ValueError):
            await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                             tradition=f"Isaiah{self.nbr}",
                                             note="Demo manuscript",
                                             user="test_user")

    async def test_insert_manuscript_missing_tradition(self):
        """Test the failed insertion of a manuscript within the database
        with an unknown tradition.
        """
        with self.assertRaises(ValueError):
            await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                             tradition=f"Isaiah{self.nbr}",
                                             note="Demo manuscript",
                                             user="test_user")

    async def test_insert_folio(self):
        """Test the insertion of a folio within the database.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        # Check that no error is raised when inserting the folio
        folio = await self.client.fetch_folio_id(
            manuscript=f"A{self.nbr}",
            tradition=f"Isaiah{self.nbr}",
            folio=f"{self.nbr}",)
        try:
            self.assertIsNotNone(folio)
        except Exception as e:
            self.fail(f"Folio not inserted: {e}")

    async def test_insert_folio_already_exists(self):
        """
        Test the insertion of a folio within the database that already exists.
        """
        with self.assertRaises(ValueError):
            await self.client.add_folio(manuscript=f"A{self.nbr}",
                                        tradition=f"Isaiah{self.nbr}",
                                        folio="1",
                                        position_in_manuscript=1,
                                        user="test_user")

    async def test_insert_folio_missing_manuscript(self):
        """Tests the failed insertion of a folio within the database when the
        manuscript does not exist in the database.
        """
        with self.assertRaises(ValueError):
            await self.client.add_folio(manuscript=f"A{self.nbr}",
                                        tradition=f"Isaiah{self.nbr}",
                                        folio="1",
                                        position_in_manuscript=1,
                                        user="test_user")

    async def test_insert_folio_missing_tradition(self):
        """Tests the failed insertion of a folio within the database when the
        tradition does not exist in the database.
        """
        with self.assertRaises(ValueError):
            await self.client.add_folio(manuscript=f"A{self.nbr}",
                                        tradition=f"Isaiah{self.nbr}",
                                        folio="1",
                                        position_in_manuscript=1,
                                        user="test_user")

    async def test_insert_column_success(self):
        """Test the insertion of a column within the database as a success.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        # Check that no error is raised when inserting the column
        column = await self.client.fetch_column_id(column_position=1,
                                                   tradition=f"Isaiah{self.nbr}",
                                                   manuscript=f"A{self.nbr}",
                                                   folio=f"{self.nbr}",
                                                   user="test_user")
        try:
            self.assertIsNotNone(column)
        except Exception as e:
            self.fail(f"Column not inserted: {e}")

    async def test_insert_line(self):
        """Test the insertion of a line within the database.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")

        # Check that no error is raised when inserting the line
        line = await self.client.fetch_line_id(
            manuscript=f"A{self.nbr}",
            tradition=f"Isaiah{self.nbr}",
            folio=f"{self.nbr}",
            column=1,
            line=1)
        try:
            self.assertIsNotNone(line)
        except Exception as e:
            self.fail(f"Line not inserted: {e}")

    async def test_insert_line_already_exists(self):
        """Test the failed insertion of a line within the database when it already exists.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        with self.assertRaises(ValueError):
            await self.client.add_line(manuscript=f"A{self.nbr}",
                                       tradition=f"Isaiah{self.nbr}",
                                       folio=f"{self.nbr}",
                                       column_position_in_folio=1,
                                       position_in_column=1,
                                       user="test_user")

    async def test_insert_line_missing_folio(self):
        """Test the failed insertion of a line within the database when the folio does not exist.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        with self.assertRaises(ValueError):
            await self.client.add_line(manuscript=f"A{self.nbr}",
                                       tradition=f"Isaiah{self.nbr}",
                                       folio=f"unknown",
                                       column_position_in_folio=1,
                                       position_in_column=1,
                                       user="test_user")

    async def test_insert_chapter(self):
        """
        Test the insertion of a chapter within the database.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        # Check that no error is raised when inserting the chapter
        chapter = await self.client.fetch_chapter_id(tradition=f"Isaiah{self.nbr}",
                                                     chapter=self.nbr)
        try:
            self.assertIsNotNone(chapter)
        except Exception as e:
            self.fail(f"Chapter not inserted: {e}")

    async def test_insert_chapter_already_exists(self):
        """Test the failed insertion of a chapter within the database when it already exists.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        with self.assertRaises(ValueError):
            await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                          chapter=self.nbr,
                                          user="test_user")

    async def test_insert_chapter_missing_tradition(self):
        """Test the failed insertion of a chapter within the database when the tradition does not exist.
        """
        with self.assertRaises(ValueError):
            await self.client.add_chapter(tradition="unknown",
                                          chapter=self.nbr,
                                          user="test_user")

    async def test_insert_verse(self):
        """Test the insertion of a version within the database.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        await self.client.add_verse(tradition=f"Isaiah{self.nbr}",
                                    chapter=self.nbr,
                                    verse=f"{self.nbr}",
                                    user="test_user")
        # Check that no error is raised when inserting the verse
        verse = await self.client.fetch_verse_id(tradition=f"Isaiah{self.nbr}",
                                                 chapter=self.nbr,
                                                 verse=f"{self.nbr}")
        try:
            self.assertIsNotNone(verse)
        except Exception as e:
            self.fail(f"Verse not inserted: {e}")

    async def test_insert_verse_already_exists(self):
        """Test the failed insertion of a verse within the database when it already exists.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        await self.client.add_verse(tradition=f"Isaiah{self.nbr}",
                                    chapter=self.nbr,
                                    verse=f"{self.nbr}",
                                    user="test_user")
        with self.assertRaises(ValueError):
            await self.client.add_verse(tradition=f"Isaiah{self.nbr}",
                                        chapter=self.nbr,
                                        verse=f"{self.nbr}",
                                        user="test_user")

    async def test_insert_verse_missing_chapter(self):
        """Test the failed insertion of a verse within the database when the chapter does not exist.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        with self.assertRaises(ValueError):
            await self.client.add_verse(tradition=f"Isaiah{self.nbr}",
                                        chapter=self.nbr,
                                        verse=f"{self.nbr}",
                                        user="test_user")

    async def test_insert_content_no_chap(self):
        """Test the insertion of content within the database when no chapter is specified.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        await self.client.add_readings(manuscript=f"A{self.nbr}",
                                       tradition=f"Isaiah{self.nbr}",
                                       folio=f"{self.nbr}",
                                       line=1,
                                       column=1,
                                       content="εν αρκη ετελεσεν ο θεος τον ουρανον και την γην",
                                       user="test_user")
        # TODO: check proper insertion of the readings when verse are mentioned

    def test_itemize_readings(self):
        """Test the itemization of readings.
        """
        readings = "<w>εν</w> <w>αρχη</w>"
        readings = self.client._itemize_readings(readings)
        print(
            readings
        )
        self.assertCountEqual(readings, [
            {'position_in_line': 1, 'reading': '<w>', 'is_xml': True},
            {'position_in_line': 2,
             'reading': 'εν', 'is_xml': False},
            {'position_in_line': 3,
             'reading': '</w>', 'is_xml': True},
            {'position_in_line': 4,
             'reading': ' ', 'is_xml': False},
            {'position_in_line': 5,
             'reading': '<w>', 'is_xml': True},
            {'position_in_line': 6,
             'reading': 'αρχη', 'is_xml': False},
            {'position_in_line': 7, 'reading': '</w>', 'is_xml': True}])

    async def test_insert_content_chap_verse(self):
        """Test the insertion of content within the database when a chapter and verse are specified.
        """

        # TODO: check proper insertion of the readings

    async def test_remove_tradition(self):
        """
        Test the removal of a tradition from the database.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.remove_tradition(tradition=f"Isaiah{self.nbr}", user="test_user")
        with self.assertRaises(ValueError):
            await self.client.fetch_tradition_id(f"Isaiah{self.nbr}")

    async def test_remove_tradition_missing(self):
        """
        Test the failed removal of a tradition from the database when it does not exist.
        """
        with self.assertRaises(ValueError):
            await self.client.remove_tradition(tradition=f"Isaiah{self.nbr}", user="test_user")

    async def test_remove_manuscript(self):
        """
        Tests the removal of a manuscript from the database.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.remove_manuscript(manuscript=f"A{self.nbr}", tradition=f"Isaiah{self.nbr}", user="test_user")
        with self.assertRaises(ValueError):
            await self.client.fetch_manuscript_id(manuscript=f"A{self.nbr}", tradition=f"Isaiah{self.nbr}")

    async def test_remove_manuscript_missing(self):
        """
        Test the failed removal of a manuscript from the database when it does not exist.
        """
        with self.assertRaises(ValueError):
            await self.client.remove_manuscript(manuscript=f"A{self.nbr}", tradition=f"Isaiah{self.nbr}", user="test_user")

    async def test_remove_folio(self):
        """Tests that removing folios behaves as expected.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.remove_folio(manuscript=f"A{self.nbr}",
                                       tradition=f"Isaiah{self.nbr}",
                                       folio=f"{self.nbr}",
                                       user="test_user")
        with self.assertRaises(ValueError):
            await self.client.fetch_folio_id(manuscript=f"A{self.nbr}",
                                             tradition=f"Isaiah{self.nbr}",
                                             folio=f"{self.nbr}")

    async def test_remove_folio_missing(self):
        """Test the failed removal of a folio from the database when it does not exist.
        """
        with self.assertRaises(ValueError):
            await self.client.remove_folio(manuscript=f"A{self.nbr}",
                                           tradition=f"Isaiah{self.nbr}",
                                           folio=f"{self.nbr}",
                                           user="test_user")

    async def test_remove_line(self):
        """Tests that removing lines behaves as expected.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        await self.client.remove_line(manuscript=f"A{self.nbr}",
                                      tradition=f"Isaiah{self.nbr}",
                                      folio=f"{self.nbr}",
                                      column_position_in_folio=1,
                                      line=1,
                                      user="test_user")

        with self.assertRaises(ValueError):
            await self.client.fetch_line_id(manuscript=f"A{self.nbr}",
                                            tradition=f"Isaiah{self.nbr}",
                                            folio=f"{self.nbr}",
                                            line=1,
                                            column=1)

    async def test_remove_chapter(self):
        """Tests that removing chapters behaves as expected.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        await self.client.remove_chapter(tradition=f"Isaiah{self.nbr}",
                                         chapter=self.nbr,
                                         user="test_user")
        with self.assertRaises(ValueError):
            await self.client.fetch_chapter_id(tradition=f"Isaiah{self.nbr}",
                                               chapter=self.nbr)

    async def test_remove_chapter_missing(self):
        """Test the failed removal of a chapter from the database when it does not exist.
        """
        with self.assertRaises(ValueError):
            await self.client.remove_chapter(tradition=f"Isaiah{self.nbr}",
                                             chapter=self.nbr,
                                             user="test_user")

    async def test_remove_verse(self):
        """Tests that removing verses behaves as expected.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        await self.client.add_verse(tradition=f"Isaiah{self.nbr}",
                                    chapter=self.nbr,
                                    verse=f"{self.nbr}",
                                    user="test_user")
        await self.client.remove_verse(tradition=f"Isaiah{self.nbr}",
                                       chapter=self.nbr,
                                       verse=f"{self.nbr}",
                                       user="test_user")
        with self.assertRaises(ValueError):
            await self.client.fetch_verse_id(tradition=f"Isaiah{self.nbr}",
                                             chapter=self.nbr,
                                             verse=f"{self.nbr}")

    async def test_remove_verse_missing(self):
        """Test the failed removal of a verse from the database when it does not exist.
        """
        with self.assertRaises(ValueError):
            await self.client.remove_verse(tradition=f"Isaiah{self.nbr}",
                                           chapter=self.nbr,
                                           verse=f"{self.nbr}",
                                           user="test_user")

    async def test_add_verse_notes(self):
        """Test the addition of notes to a verse.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        await self.client.add_verse(tradition=f"Isaiah{self.nbr}",
                                    chapter=self.nbr,
                                    verse=f"{self.nbr}",
                                    user="test_user")
        await self.client.add_verse_notes(tradition=f"Isaiah{self.nbr}",
                                          chapter=self.nbr,
                                          verse=f"{self.nbr}",
                                          note="This is a note regarding a verse",
                                          user="test_user")
        # TODO: once functions for fetching are developed test that note is properly written

    async def test_remove_verse_notes(self):
        """Test the removal of notes from a verse.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_chapter(tradition=f"Isaiah{self.nbr}",
                                      chapter=self.nbr,
                                      user="test_user")
        await self.client.add_verse(tradition=f"Isaiah{self.nbr}",
                                    chapter=self.nbr,
                                    verse=f"{self.nbr}",
                                    user="test_user")
        await self.client.add_verse_notes(tradition=f"Isaiah{self.nbr}",
                                          chapter=self.nbr,
                                          verse=f"{self.nbr}",
                                          note="This is a note regarding a verse",
                                          user="test_user")
        await self.client.remove_verse_notes(tradition=f"Isaiah{self.nbr}",
                                             chapter=self.nbr,
                                             verse=f"{self.nbr}",
                                             user="test_user")

    async def test_add_reading_note(self):
        """
        Test the addition of a note to a reading.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        await self.client.add_readings(manuscript=f"A{self.nbr}",
                                       tradition=f"Isaiah{self.nbr}",
                                       folio=f"{self.nbr}",
                                       line=1,
                                       column=1,
                                       content="".join(
                                           ["<w>{}</w>".format(word) for word in "εν αρκη ετελεσεν ο θεος τον ουρανον και την γην".split()]),
                                       user="test_user")
        await self.client.add_reading_notes(manuscript=f"A{self.nbr}",
                                            tradition=f"Isaiah{self.nbr}",
                                            folio=f"{self.nbr}",
                                            line=1,
                                            column=1,
                                            reading="εν",
                                            position_in_line=2,
                                            category="translation",
                                            note="This is a note regarding a reading",
                                            user="test_user")

    async def test_remove_reading_note(self):
        """
        Test the removal of a note from a reading.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        await self.client.add_readings(manuscript=f"A{self.nbr}",
                                       tradition=f"Isaiah{self.nbr}",
                                       folio=f"{self.nbr}",
                                       line=1,
                                       column=1,
                                       content="".join(
                                           ["<w>{}</w>".format(word) for word in "εν αρκη ετελεσεν ο θεος τον ουρανον και την γην".split()]),
                                       user="test_user")
        await self.client.add_reading_notes(manuscript=f"A{self.nbr}",
                                            tradition=f"Isaiah{self.nbr}",
                                            folio=f"{self.nbr}",
                                            line=1,
                                            column=1,
                                            reading="εν",
                                            category="translation",
                                            position_in_line=2,
                                            note="This is a note regarding a reading",
                                            user="test_user")
        await self.client.remove_reading_notes(manuscript=f"A{self.nbr}",
                                               tradition=f"Isaiah{self.nbr}",
                                               folio=f"{self.nbr}",
                                               line=1,
                                               column=1,
                                               reading="εν",
                                               category="translation",
                                               position_in_line=2,
                                               user="test_user")

    async def test_add_line_notes(self):
        """
        Test the addition of notes to a line.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        await self.client.add_line_notes(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         folio=f"{self.nbr}",
                                         line=1,
                                         column=1,
                                         note="This is a note regarding a line",
                                         user="test_user")

    async def test_remove_line_notes(self):
        """
        Test the removal of notes from a line.
        """
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        await self.client.add_line_notes(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         folio=f"{self.nbr}",
                                         line=1,
                                         column=1,
                                         note="This is a note regarding a line",
                                         user="test_user")
        await self.client.remove_line_notes(manuscript=f"A{self.nbr}",
                                            tradition=f"Isaiah{self.nbr}",
                                            folio=f"{self.nbr}",
                                            line=1,
                                            column=1,
                                            user="test_user")


class TestDBFetch(TestSCRIBESClient):
    """Test all data fetch within the database.
    """

    async def test_get_tradition(self):
        """Tests that fetching all traditions behaves as expected.
        """
        # Drop all traditions
        await self.client.database.execute(query="DELETE FROM traditions")
        # Add new tradition
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        traditions = await self.client.get_traditions(archived=0, user="test_user")
        self.assertEqual(traditions, [f"Isaiah{self.nbr}"])

    async def test_get_tradition_missing(self):
        """
        Test the failed fetching of traditions from the database when none exist.
        """
        # Drop all traditions
        await self.client.database.execute(query="DELETE FROM traditions")
        with self.assertRaises(ValueError):
            await self.client.get_traditions(archived=0, user="test_user")

    async def test_get_manuscripts(self):
        """
        Tests that fetching all manuscripts behaves as expected.
        """
        # Drop all manuscripts
        await self.client.database.execute(query="DELETE FROM manuscripts")
        # Add new manuscript
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        manuscripts = await self.client.get_traditions_manuscripts(tradition=f"Isaiah{self.nbr}",
                                                                   archived=0,
                                                                   user="test_user")
        self.assertEqual(manuscripts, [f"A{self.nbr}"])

    async def test_get_manuscripts_missing(self):
        """Tests that fetching the manuscripts when there is none in the database
        raises a ValueError.
        """
        # Drop all manuscripts
        await self.client.database.execute(query="DELETE FROM manuscripts")
        with self.assertRaises(ValueError):
            await self.client.get_traditions_manuscripts(tradition=f"Isaiah{self.nbr}",
                                                         archived=0,
                                                         user="test_user")

    async def test_get_folios(self):
        """Tests that fetching all folios behaves as expected.
        """
        # Drop all folios
        await self.client.database.execute(query="DELETE FROM folios")
        # Add new folio
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        folios = await self.client.get_manuscripts_folios(manuscript=f"A{self.nbr}",
                                                          tradition=f"Isaiah{self.nbr}",
                                                          user="test_user")
        self.assertEqual(folios, [{'folio_name': str(self.nbr),
                                   'image_url': 'NULL'}])

    async def test_get_folios_missing(self):
        """Tests that fetching the folios when there is none in the database
        raises a ValueError.
        """
        # Drop all folios
        await self.client.database.execute(query="DELETE FROM folios")
        with self.assertRaises(ValueError):
            await self.client.get_manuscripts_folios(manuscript=f"A{self.nbr}",
                                                     tradition=f"Isaiah{self.nbr}",
                                                     user="test_user")

    async def test_get_folio_readings(self):
        """Tests that fetching all readings for a folio behaves as expected.
        """
        # Drop all readings
        await self.client.database.execute(query="DELETE FROM readings")
        # Add new readings
        await self.client.add_tradition(tradition=f"Isaiah{self.nbr}",
                                        note="Demo tradition",
                                        is_public=True,
                                        user="test_user")
        await self.client.add_manuscript(manuscript=f"A{self.nbr}",
                                         tradition=f"Isaiah{self.nbr}",
                                         note="Demo manuscript",
                                         user="test_user")
        await self.client.add_folio(manuscript=f"A{self.nbr}",
                                    tradition=f"Isaiah{self.nbr}",
                                    folio=f"{self.nbr}",
                                    position_in_manuscript=1,
                                    user="test_user")
        await self.client.add_column(tradition=f"Isaiah{self.nbr}",
                                     manuscript=f"A{self.nbr}",
                                     folio=f"{self.nbr}",
                                     position_in_folio=1,
                                     user="test_user")
        await self.client.add_line(manuscript=f"A{self.nbr}",
                                   tradition=f"Isaiah{self.nbr}",
                                   folio=f"{self.nbr}",
                                   column_position_in_folio=1,
                                   position_in_column=1,
                                   user="test_user")
        await self.client.add_readings(manuscript=f"A{self.nbr}",
                                       tradition=f"Isaiah{self.nbr}",
                                       folio=f"{self.nbr}",
                                       line=1,
                                       column=1,
                                       content="εν αρκη ετελεσεν ο θεος τον ουρανον και την γην",
                                       user="test_user")
        readings = await self.client.get_folio_readings(manuscript=f"A{self.nbr}",
                                                        tradition=f"Isaiah{self.nbr}",
                                                        folio=f"{self.nbr}",
                                                        user="test_user")
        self.assertEqual(readings, [
                         {'line': 1, 'content': 'εν αρκη ετελεσεν ο θεος τον ουρανον και την γην'}])

    async def test_add_chapter_verse(self):
        """Tests that adding a chapter and a verse to the.
        """
        # TODO


class TestDBUpdate(TestSCRIBESClient):
    """Test all data update within the database.
    """


# TODO: freeze data once input is stable to dump


if __name__ == "__main__":
    unittest.main()

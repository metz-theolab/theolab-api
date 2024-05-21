"""DB client to fetch textual data from the SCRIBES API.
"""
from backend.tools.sql_client import SQLClient
import re
from typing import Optional
from asyncpg.exceptions import UniqueViolationError
from loguru import logger


class SCRIBESBaseClient(SQLClient):
    """Base client for manipulation of SCRIBES data.
    """
    async def fetch_user_groups(self,
                                username: str):
        """Given a username, return the corresponding groups IDs.
        """
        query = self.format_query(f"""
            SELECT group_id
            FROM permissions_traditions
            WHERE permissions_traditions.user={username}
        """)
        usergroup = await self.database.fetch_one(query=query)
        if not usergroup:
            raise ValueError(
                f"Username {username} not associated with any group.")
        return usergroup[0]

    async def fetch_tradition_id(self,
                                 tradition: str,
                                 user: Optional[str] = None):
        """
        Fetch tradition ID from the database.
        """
        query = f"""
            SELECT traditions.id
            FROM traditions
            LEFT JOIN permissions ON traditions.id = permissions.tradition_id
            WHERE tradition_name = '{tradition}'
            AND (is_public=TRUE
        """
        if user:
            query += f" OR created_by='{user}' OR permissions.user='{user}')"
        else:
            query += ")"
        record = await self.database.fetch_one(query=self.format_query(query))
        if not record:
            raise ValueError(
                f"Tradition {tradition} not found for user {user}.")
        return record[0]

    async def fetch_manuscript_id(self,
                                  tradition: str,
                                  manuscript: str,
                                  user: Optional[str] = None):
        """
        Fetch manuscript ID from the database.
        """
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition,
                                                         user=user)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e
        query = self.format_query(f"""
        SELECT id
        FROM manuscripts
        WHERE tradition_id = {tradition_id} AND manuscript_name = '{manuscript}'
        """)
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(f"Manuscript {manuscript} not found.")
        return record[0]

    async def fetch_folio_id(
            self,
            tradition: str,
            manuscript: str,
            folio: str,
            user: Optional[str] = None
    ):
        """Given a folio name within a manuscript and a tradition fetch its ID.
        """
        try:
            manuscript_id = await self.fetch_manuscript_id(
                tradition=tradition,
                manuscript=manuscript,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Manuscript {manuscript} not found for tradition {tradition}.") from e
        query = self.format_query(f"""
            SELECT id
            FROM folios
            WHERE manuscript_id = {manuscript_id} AND folio_name = '{folio}'
            """)
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} in tradition {tradition}.")
        return record[0]

    async def fetch_chapter_id(
            self,
            tradition: str,
            chapter: int,
            user: Optional[str] = None):
        """Given a chapter name within a manuscript and a tradition fetch its ID.
        """
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition, user=user)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e
        query = self.format_query(f"""
            SELECT id
            FROM chapters
            WHERE tradition_id = {tradition_id} AND chapter_number = {chapter}
        """)
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(
                f"Chapter {chapter} not found for tradition {tradition}.")
        return record[0]

    async def fetch_line_id(
            self,
            tradition: str,
            manuscript: str,
            folio: str,
            column: int,
            line: int,
            user: Optional[str] = None):
        """Given a line number within a manuscript, a tradition and a folio fetch its ID."""
        try:
            column_id = await self.fetch_column_id(
                tradition=tradition,
                manuscript=manuscript,
                column_position=column,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} in tradition {tradition}.") from e

        query = self.format_query(f"""
            SELECT id
            FROM column_lines
            WHERE column_id = {column_id} AND position_in_column = {line}
        """)
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(
                f"Line {line} not found for column {column_id} of folio {folio} in manuscript {manuscript}"
                f" in tradition {tradition}.")
        return record[0]

    async def fetch_verse_id(
            self,
            tradition: str,
            chapter: int,
            verse: str,
            user: Optional[str] = None):
        """Fetch the verse ID from the database.
        """
        try:
            chapter_id = await self.fetch_chapter_id(
                tradition=tradition,
                chapter=chapter,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Chapter {chapter} not found for tradition {tradition}.") from e
        query = self.format_query(f"""
            SELECT id
            FROM verses
            WHERE chapter_id = {chapter_id} AND verse_number = {verse}
        """)
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(
                f"Verse {verse} not found for chapter {chapter} in tradition {tradition}.")
        return record[0]

    async def fetch_column_id(
            self,
            column_position: int,
            tradition: str,
            manuscript: str,
            folio: str,
            user: Optional[str] = None):
        """Fetch the column ID from the database.
        """
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user)
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} in tradition {tradition}") from e

        query = self.format_query(f"""
            SELECT id
            FROM columns
            WHERE folio_id = {folio_id}
            AND position_in_folio = {column_position}
        """)
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(
                f"Column not find column in position {column_position} for folio "
                f"in manuscript {manuscript} in tradition {tradition}.")
        return record[0]


class SCRIBESCreateDelete(SCRIBESBaseClient):
    """Methods to create and delete data from the SCRIBES database.
    """
    async def add_user_tradition(self,
                                 tradition: str,
                                 username: str,
                                 user: str):
        """Add a new user username to a tradition."""
        # Fetch the tradition ID
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition, user=user)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e
        query = self.format_query(f"""
        INSERT INTO permissions (tradition_id, "user")
        SELECT {tradition_id}, '{username}'
        FROM traditions
        WHERE created_by = '{user}' AND id = {tradition_id};
        """
                                  )
        task = await self.database.execute(query=query)
        if task == 0:
            logger.error(
                f"User {user} does not have the rights to add users to tradition {tradition}.")
            raise ValueError(
                f"User {user} does not have the rights to add users to tradition {tradition}.")
        else:
            logger.info(f"Added user {username} to tradition {tradition_id}.")

    async def add_manuscript(self,
                             manuscript: str,
                             tradition: str,
                             note: str,
                             user: str):
        """
        Add a manuscript to the database.
        """
        # Fetch the tradition ID
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition, user=user)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e
        # Query to add the manuscript data
        query = self.format_query(f"""
        INSERT INTO manuscripts (manuscript_name, tradition_id, created_by, note)
        VALUES('{manuscript}', {tradition_id}, '{user}', '{note}')
        """)
        try:
            await self.database.execute(query=query)
            logger.info(f"Manuscript {manuscript} added to the database.")
        except UniqueViolationError as e:
            raise ValueError(
                f"Manuscript {manuscript} already exists for tradition {tradition}.") from e

    async def remove_manuscript(self,
                                manuscript: str,
                                tradition: str,
                                user: str):
        """
        Remove a manuscript from the database.
        """
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition, user=user)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e

        query = self.format_query(f"""
        DELETE FROM manuscripts WHERE manuscript_name = '{manuscript}' AND tradition_id = {tradition_id} AND created_by = '{user}' RETURNING *""")
        records = await self.database.execute(query=query)
        if records:
            logger.info(f"Manuscript {manuscript} removed from the database.")
        else:
            logger.info(f"Manuscript {manuscript} not found in the database.")
            raise ValueError(f"Manuscript {manuscript} not found.")

    async def add_folio(self,
                        tradition: str,
                        manuscript: str,
                        folio: str,
                        position_in_manuscript: int,
                        user: str,
                        image_url: str = "NULL",
                        ):
        """
        Add a folio to the database.
        """
        # Check if the manuscript exist
        try:
            manuscript_id = await self.fetch_manuscript_id(
                tradition=tradition,
                manuscript=manuscript,
                user=user
            )
        except ValueError as e:
            raise ValueError(f"Manuscript {manuscript} not found.") from e
        query = self.format_query(f"""
        INSERT INTO folios (created_by, manuscript_id, folio_name, position_in_manuscript, image_url)
        VALUES ('{user}', {manuscript_id}, '{folio}', {position_in_manuscript}, '{image_url}')
        """)
        try:
            await self.database.execute(query=query)
            logger.info(f"Folio {folio} added to the database.")
        except UniqueViolationError as e:
            raise ValueError(
                f"Folio {folio} already exists for manuscript {manuscript}") from e

    async def remove_folio(self,
                           tradition: str,
                           manuscript: str,
                           folio: str,
                           user: str):
        """
        Remove a folio from the database.
        """
        try:
            manuscript_id = await self.fetch_manuscript_id(
                tradition=tradition,
                manuscript=manuscript,
                user=user
            )
        except ValueError as e:
            raise ValueError(f"Manuscript {manuscript} not found.") from e
        query = self.format_query(f"""
        DELETE FROM folios WHERE folio_name = '{folio}' AND
        manuscript_id = {manuscript_id} AND created_by = '{user}' RETURNING *
        """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(f"Folio {folio} removed from the database.")
        else:
            logger.info(f"Folio {folio} not found in the database.")
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript}.")

    async def add_tradition(self,
                            tradition: str,
                            note: str,
                            is_public: bool,
                            user: str):
        """
        Add a tradition to the database.
        """
        query = self.format_query(f"""
        INSERT INTO traditions (tradition_name, created_by, note, is_public)
        VALUES('{tradition}', '{user}', '{note}', {is_public})
        """)
        try:
            await self.database.execute(query=query)
            logger.info(f"Tradition {tradition} added to the database.")
        except UniqueViolationError as e:
            raise ValueError(f"Tradition {tradition} already exists.") from e

    async def remove_tradition(self,
                               tradition: str,
                               user: str):
        """
        Remove a tradition from the database.
        """
        query = self.format_query(f"""
        DELETE FROM traditions WHERE tradition_name = '{tradition}' AND created_by = '{user}' RETURNING *
        """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(f"Tradition {tradition} removed from the database.")
        else:
            logger.info(f"Tradition {tradition} not found in the database.")
            raise ValueError(f"Tradition {tradition} not found.")

    async def add_chapter(self,
                          tradition: str,
                          chapter: int,
                          user: str):
        """
        Add a chapter to the database.
        """
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition, user=user)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e
        query = f"""
        INSERT INTO chapters (created_by, chapter_number, tradition_id)
        VALUES('{user}', {chapter}, {tradition_id})
        """
        try:
            await self.database.execute(query=query)
            logger.info(f"Chapter {chapter} added to the database.")
        except UniqueViolationError as e:
            raise ValueError(
                f"Chapter {chapter} already exists for tradition {tradition}.") from e

    async def remove_chapter(self,
                             tradition: str,
                             chapter: int,
                             user: str):
        """
        Remove a chapter from the database.
        """
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e
        query = self.format_query(f"""
        DELETE FROM chapters WHERE chapter_number = {chapter} AND tradition_id = {tradition_id} AND created_by = '{user}' RETURNING *
        """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(f"Chapter {chapter} removed from the database.")
        else:
            logger.info(f"Chapter {chapter} not found in the database.")
            raise ValueError(
                f"Chapter {chapter} not found for tradition {tradition}.")

    async def add_verse(self,
                        tradition: str,
                        chapter: int,
                        verse: str,
                        user: str):
        """Add a verse to the database.
        """
        try:
            chapter_id = await self.fetch_chapter_id(
                tradition=tradition,
                chapter=chapter,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Chapter {chapter} not found for tradition {tradition}.") from e
        query = f"""
        INSERT INTO verses (created_by, verse_number, chapter_id)
        VALUES('{user}', '{verse}', {chapter_id})
        """
        try:
            await self.database.execute(query=query)
            logger.info(f"Verse {verse} added to the database.")
        except UniqueViolationError as e:
            raise ValueError(
                f"Verse {verse} already exists for chapter {chapter} in tradition {tradition}.") from e

    async def remove_verse(self,
                           tradition: str,
                           chapter: int,
                           verse: str,
                           user: str):
        """
        Remove a verse from the database.
        """
        try:
            chapter_id = await self.fetch_chapter_id(
                tradition=tradition,
                chapter=chapter,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Chapter {chapter} not found for tradition {tradition}.") from e
        query = self.format_query(f"""
        DELETE FROM verses WHERE verse_number = {verse} AND chapter_id = {chapter_id} AND created_by = '{user}' RETURNING *
        """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(f"Verse {verse} removed from the database.")
        else:
            logger.info(f"Verse {verse} not found in the database.")
            raise ValueError(
                f"Verse {verse} not found for chapter {chapter} in tradition {tradition}.")

    async def add_column(self,
                         tradition: str,
                         manuscript: str,
                         position_in_folio: int,
                         folio: str,
                         user: str):
        """Add a new column to the database.
        """
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
        INSERT INTO columns (created_by, folio_id, position_in_folio)
        VALUES('{user}', {folio_id}, {position_in_folio})
        """)
        try:
            await self.database.execute(query=query)
            logger.info(
                f"Column {position_in_folio} added to the database for folio {folio} of manuscript {manuscript} of tradition {tradition}.")
        except UniqueViolationError as e:
            raise ValueError(
                f"Column {position_in_folio} already exists for folio {folio} in manuscript {manuscript} in tradition {tradition}.") from e

    async def remove_column(self,
                            tradition: str,
                            manuscript: str,
                            position_in_folio: int,
                            folio: str,
                            user: str):
        """Remove a column from the database.
        """
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
        DELETE FROM columns WHERE position_in_folio = {position_in_folio} AND folio_id = {folio_id} AND created_by = '{user}' RETURNING *
        """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(
                f"Column {position_in_folio} of folio {folio} for manuscript {manuscript} removed from the database.")
        else:
            logger.info(
                f"Column {position_in_folio} of folio {folio} for manuscript {manuscript} not found in the database.")
            raise ValueError(
                f"Column {position_in_folio} not found for folio {folio} in manuscript {manuscript} in tradition {tradition}.")

    async def add_line(self,
                       tradition: str,
                       manuscript: str,
                       folio: str,
                       position_in_column: int,
                       column_position_in_folio: int,
                       user: str):
        """
        Add a line to the database.
        """
        try:
            column_id = await self.fetch_column_id(
                tradition=tradition,
                manuscript=manuscript,
                column_position=column_position_in_folio,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Column {column_position_in_folio} not found for folio {folio}")

        query = self.format_query(f"""
        INSERT INTO column_lines (created_by, column_id, position_in_column)
        VALUES('{user}', {column_id}, {position_in_column})
        """)
        try:
            await self.database.execute(query=query)
            logger.info(f"Line {position_in_column} added to the database.")
        except UniqueViolationError as e:
            raise ValueError(
                f"Line {position_in_column} already exists for folio {folio} in manuscript {folio} in tradition {tradition}.") from e

    async def remove_line(self,
                          tradition: str,
                          manuscript: str,
                          folio: str,
                          column_position_in_folio: int,
                          position_in_column: int,
                          user: str):
        """
        Remove a line from the database.
        """
        try:
            column_id = await self.fetch_column_id(
                tradition=tradition,
                manuscript=manuscript,
                column_position=column_position_in_folio,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Column {column_position_in_folio} not found for folio {folio}")
        query = self.format_query(f"""
        DELETE FROM column_lines WHERE position_in_column = {position_in_column} AND column_id = {column_id} AND created_by = '{user}' RETURNING *
        """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(
                f"Line {position_in_column} removed from the database.")
        else:
            logger.info(
                f"Line {position_in_column} not found in the database.")
            raise ValueError(
                f"Line {position_in_column} not found for column {column_position_in_folio} folio {folio} in manuscript {manuscript} in tradition {tradition}.")

    @staticmethod
    def _itemize_readings(
            content: str
    ):
        """Given a string of content, itemize the readings of the string for proper
        storage.

        #TODO: add the verse analysis, for now, stuck to 1.
        """
        itemized_readings = []
        split_string = re.findall(r"(<.*?>)|(.+?(?=<|$))", content)
        for ix, string in enumerate(split_string):
            itemized_readings.append({"position_in_line": ix + 1,
                                      "reading": "".join(string),
                                      "is_xml": "<" in "".join(string) or ">" in "".join(string)})
        return itemized_readings

    async def add_readings(self,
                           content: str,
                           tradition: str,
                           manuscript: str,
                           folio: str,
                           line: int,
                           column: int,
                           user: str,
                           chapter: Optional[int] = None,
                           verse: Optional[str] = None,
                           ):
        """Write content as readings to the database.
        Content is added to the database on a line per line basis.
        """
        try:
            line_id = await self.fetch_line_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                line=line,
                column=column,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Line {line} not found for folio {folio} in manuscript {manuscript} in tradition {tradition}.") from e
        if chapter:
            if not verse:
                raise ValueError(
                    "Cannot append content to chapter without verse.")
            try:
                verse_id = await self.fetch_verse_id(
                    tradition=tradition,
                    chapter=chapter,
                    verse=verse,
                    user=user
                )
            except ValueError as e:
                raise ValueError(
                    f"Verse {verse} not found for chapter {chapter} in tradition {tradition}.") from e
        else:
            verse_id = 'NULL'
        itemized_readings = self._itemize_readings(content)
        # Recursively append data to the database
        for item in itemized_readings:
            # TODO : adding the readings to the verse is broken and not implemented !!!
            query = self.format_query(f"""
                    INSERT INTO readings (reading, created_by, line_id, verse_id, position_in_line, position_in_verse, is_xml)
                    VALUES ('{item["reading"]}', '{user}', {line_id}, {verse_id}, {item["position_in_line"]}, {item["position_in_line"]}, {item["is_xml"]})
                    """)
            query = self.format_query(query)
            await self.database.execute(query=query)
        logger.info(
            f"Inserted {len(itemized_readings)} readings to the database.")

    async def fetch_reading_id(self,
                               tradition: str,
                               manuscript: str,
                               folio: str,
                               column: int,
                               line: int,
                               reading: str,
                               position_in_line: int,
                               user: Optional[str] = None):
        """Fetch the reading ID from the database.
        """
        try:
            line_id = await self.fetch_line_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                line=line,
                column=column,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Line {line} not found for folio {folio} in manuscript {manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
            SELECT id
            FROM readings
            WHERE line_id = {line_id} AND reading = '{reading}' AND position_in_line = {position_in_line}
        """)
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(
                f"Reading {reading} not found for line {line} at position {position_in_line}.")
        return record[0]

    async def add_line_notes(self,
                             note: str,
                             line: int,
                             tradition: str,
                             manuscript: str,
                             column: int,
                             folio: str,
                             user: str):
        """Add a note to the database for a line."""
        try:
            line_id = await self.fetch_line_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                line=line,
                column=column,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Line {line} not found for folio {folio} in manuscript {manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
            INSERT INTO line_notes (note, line_id, created_by)
            VALUES ('{note}', {line_id}, '{user}')
            """)
        await self.database.execute(query=query)
        logger.info(f"Note {note} added to the database for line {line}.")

    async def remove_line_notes(self,
                                line: int,
                                tradition: str,
                                manuscript: str,
                                folio: str,
                                column: int,
                                user: str):
        """Remove a note from the database for a line."""
        try:
            line_id = await self.fetch_line_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                line=line,
                column=column,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Line {line} not found for folio {folio} in manuscript {manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
            DELETE FROM line_notes WHERE line_id = {line_id} AND created_by = '{user}' RETURNING *
            """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(f"Note removed from the database for line {line}.")
        else:
            logger.info(f"Note not found in the database for line {line}.")
            raise ValueError(f"Note not found for line {line}.")

    async def add_verse_notes(self, note: str, verse: str, chapter: int, tradition: str, user: str):
        """Add a note to the database for a verse."""
        try:
            verse_id = await self.fetch_verse_id(
                tradition=tradition,
                chapter=chapter,
                verse=verse,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Verse {verse} not found for chapter {chapter} in tradition {tradition}.") from e
        query = self.format_query(f"""
            INSERT INTO verse_notes (note, verse_id, created_by)
            VALUES ('{note}', {verse_id}, '{user}')
            """)
        await self.database.execute(query=query)
        logger.info(f"Note {note} added to the database for verse {verse}.")

    async def remove_verse_notes(self, verse: str, chapter: int, tradition: str, user: str):
        """Remove a note from the database for a verse."""
        try:
            verse_id = await self.fetch_verse_id(
                tradition=tradition,
                chapter=chapter,
                verse=verse,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Verse {verse} not found for chapter {chapter} in tradition {tradition}.") from e
        query = self.format_query(f"""
            DELETE FROM verse_notes WHERE verse_id = {verse_id} AND created_by = '{user}' RETURNING *
            """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(f"Note removed from the database for verse {verse}.")
        else:
            logger.info(f"Note not found in the database for verse {verse}.")
            raise ValueError(f"Note not found for verse {verse}.")

    async def add_reading_notes(self,
                                note: str,
                                reading: str,
                                column: int,
                                line: int,
                                position_in_line: int,
                                tradition: str,
                                manuscript: str,
                                folio: str,
                                category: str,
                                user: str):
        """Add a note to the database for a reading.
        Category is either reading or translation.
        """
        try:
            reading_id = await self.fetch_reading_id(
                tradition=tradition,
                manuscript=manuscript,
                column=column,
                folio=folio,
                line=line,
                position_in_line=position_in_line,
                reading=reading,
                user=user
            )
        except ValueError as e:
            raise ValueError(f"Reading {reading} not found for line {line} in folio {folio} in manuscript "
                             f"{manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
            INSERT INTO {category}_notes (note, reading_id, created_by)
            VALUES ('{note}', {reading_id}, '{user}')
            """)
        await self.database.execute(query=query)
        logger.info(
            f"Note {note} added to the database for reading {reading}.")

    async def remove_reading_notes(self,
                                   reading: str,
                                   line: int,
                                   position_in_line: int,
                                   tradition: str,
                                   manuscript: str,
                                   column: int,
                                   folio: str,
                                   category: str,
                                   user: str):
        """Remove a note from the database for a reading."""
        try:
            reading_id = await self.fetch_reading_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                column=column,
                line=line,
                position_in_line=position_in_line,
                reading=reading,
                user=user
            )
        except ValueError as e:
            raise ValueError(f"Reading {reading} not found for line {line} in folio {folio} in manuscript "
                             f"{manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
            DELETE FROM {category}_notes WHERE reading_id = {reading_id} AND created_by = '{user}' RETURNING *
            """)
        records = await self.database.execute(query=query)
        if records:
            logger.info(
                f"Note removed from the database for reading {reading}.")
        else:
            logger.info(
                f"Note not found in the database for reading {reading}.")
            raise ValueError(f"Note not found for reading {reading}.")

    async def add_chapter_verse(
            self,
            reading: str,
            position_in_line: int,
            tradition: str,
            manuscript: str,
            folio: str,
            line: int,
            chapter: int,
            column: int,
            verse: str,
            user: str
    ):
        """Add a verse
        """
        try:
            reading_id = await self.fetch_reading_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                line=line,
                reading=reading,
                column=column,
                position_in_line=position_in_line
            )
        except ValueError as e:
            logger.error(
                f"Reading {reading} not found for line {line} in folio {folio} in manuscript {manuscript} in tradition {tradition}.")
            raise ValueError(
                f"Reading {reading} not found for line {line} in folio {folio} in manuscript {manuscript} in tradition {tradition}.") from e
        try:
            verse_id = self.fetch_verse_id(
                tradition=tradition, chapter=chapter, verse=verse
            )
        except ValueError:
            # Create missing verse in DB
            logger.info(
                f"Could not find verse {verse} for chapter {chapter} in tradition {tradition}.")
            await self.add_verse(tradition=tradition, chapter=chapter, verse=verse, user=user)
        query = self.format_query(f"""
        UPDATE readings
        SET verse_id = {verse_id}, chapter_id = {chapter}
        WHERE id = {reading_id}
        """)
        await self.database.execute(query=query)
        logger.info(
            f"Added verse {verse} and chapter {chapter} to reading {reading}.")


class SCRIBESUpdate(SCRIBESBaseClient):
    """Methods to update data in the SCRIBES database.
    """
    async def update_tradition(self,
                               field: str,
                               value: str,
                               tradition: str,
                               user: str):
        """Update a field in the database.
        """
        query = self.format_query(f"""
            UPDATE traditions
            SET {field} = '{value}'
            WHERE tradition_name = '{tradition}'
            AND created_by = '{user}'
        """)
        update = await self.database.execute(query=query)
        if update > 0:
            logger.info(f"Tradition {tradition} updated.")
        else:
            logger.error(f"Tradition {tradition} could not be updated.")
            raise ValueError(f"Tradition {tradition} could not be updated.")

    async def update_manuscript(self,
                                tradition: str,
                                field: str,
                                value: str,
                                manuscript: str,
                                user: str):
        """Update a field in the database.
        """
        try:
            manuscript_id = await self.fetch_manuscript_id(
                tradition=tradition,
                manuscript=manuscript,
                user=user
            )
        except ValueError as e:
            raise ValueError(f"Manuscript {manuscript} not found.") from e
        query = self.format_query(f"""
            UPDATE manuscripts
            SET {field} = '{value}'
            WHERE id = {manuscript_id}
        """)
        result = await self.database.execute(query=query)
        if result > 0:
            logger.info(f"Manuscript {manuscript} updated.")
        else:
            logger.error(f"Mansucript {manuscript} could not be updated.")

    async def update_folio(self,
                           tradition: str,
                           manuscript: str,
                           field: str,
                           value: str,
                           folio: str,
                           user: str):
        """Update a field in the database.
        """
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} in tradition {tradition}.") from e
        query = self.format_query(f"""
        UPDATE folios
        SET {field} = '{value}'
        WHERE id = {folio_id}
        """)
        await self.database.execute(query=query)
        logger.info(f"Folio {folio} updated.")


class SCRIBESFetch(SCRIBESBaseClient):
    """Methods to fetch data from the SCRIBES database.

    #TODO : think about fetching rights within the database.
    """
    async def get_traditions(self, archived: bool, user: str):
        """Fetch all traditions from the database (as tradition names are unique,
        return unique values).
        """
        query = self.format_query(f"""
            SELECT tradition_name as name, created_by, traditions.created_at, note, is_public
            FROM traditions
            LEFT JOIN permissions ON traditions.id = permissions.tradition_id
            WHERE archived = {archived} AND (is_public=TRUE OR created_by='{user}' OR permissions.user='{user}')
        """)
        records = await self.database.fetch_all(query=query)
        if not records:
            raise ValueError("No traditions found in the database.")
        return [dict(record) for record in records]

    async def get_traditions_manuscripts(self, tradition: str, archived: bool, user: str):
        """
        Fetch all manuscripts associated with a tradition.
        """
        try:
            tradition_id = await self.fetch_tradition_id(tradition=tradition, user=user)
        except ValueError as e:
            raise ValueError(f"Tradition {tradition} not found.") from e
        query = self.format_query(f"""
            SELECT manuscript_name as name, note, manuscripts.created_at, manuscripts.created_by
            FROM manuscripts
            WHERE tradition_id = {tradition_id}
            AND archived = {archived}
        """)
        records = await self.database.fetch_all(query=query)
        if not records:
            raise ValueError(
                f"No manuscripts found for tradition {tradition}.")
        return [dict(record) for record in records]

    async def get_manuscripts_folios(self,
                                     tradition: str,
                                     manuscript: str,
                                     user: str):
        """Retrieve all folios associated with a manuscript.
        """
        try:
            manuscript_id = await self.fetch_manuscript_id(
                tradition=tradition,
                manuscript=manuscript,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Manuscript {manuscript} not found for tradition {tradition}.") from e
        query = self.format_query(f"""
                SELECT folio_name AS name, image_url, created_at, created_by
                FROM folios
                WHERE manuscript_id = {manuscript_id}
        """)
        records = await self.database.fetch_all(query=query)
        if not records:
            raise ValueError(
                f"No folios found for manuscript {manuscript} of tradition {tradition}.")
        return [dict(result) for result in records]

    @staticmethod
    def contact_line_dictionary(list_dict: list[dict[str, str]], content_type: str = "reading"):
        """Group a dictionary by its keys.
        """
        grouped_dict = {}
        for dict_ in list_dict:
            position_in_column = dict_['position_in_column']
            position_in_folio = dict_['position_in_folio']
            content = dict_[content_type]
            
            if position_in_folio not in grouped_dict:
                grouped_dict[position_in_folio] = {}
            
            grouped_dict[position_in_folio][position_in_column] = content

        return grouped_dict

    async def get_folio(self,
                             tradition: str,
                             manuscript: str,
                             folio: str,
                             user: str):
        """Retrieve all the information related to a folio."""
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} of tradition {tradition}.") from e
        query = self.format_query(f"""
            SELECT folio_name, position_in_manuscript, image_url, created_at, created_by
            FROM folios
            WHERE id = {folio_id}""")
        record = await self.database.fetch_one(query=query)
        if not record:
            raise ValueError(
                f"No content found for folio {folio} of manuscript {manuscript} of tradition {tradition}.")
        return dict(record)
    
    async def get_folio_columns(self,
                             tradition: str,
                             manuscript: str,
                             folio: str,
                             user: str):
        """Retrieve all the columns within a folio."""
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} of tradition {tradition}.") from e
        query = self.format_query(f"""
            SELECT position_in_folio
            FROM columns
            WHERE folio_id = {folio_id}""")
        records = await self.database.fetch_all(query=query)
        if not records:
            raise ValueError(
                f"No content found for folio {folio} of manuscript {manuscript} of tradition {tradition}.")
        return [dict(record) for record in records]

    async def get_folio_readings(self,
                                 tradition: str,
                                 manuscript: str,
                                 folio: str,
                                 user: str):
        """Retrieve all of the readings associated with a folio.
        """
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} of tradition {tradition}.") from e

        query = self.format_query(f"""
                SELECT reading, position_in_column, columns.position_in_folio
                FROM readings
                JOIN column_lines ON readings.line_id = column_lines.id
                JOIN columns ON column_lines.column_id = columns.id
                JOIN folios ON columns.folio_id = folios.id
                WHERE columns.folio_id = {folio_id}
                ORDER BY column_lines.column_id, position_in_line
        """)
        records = await self.database.fetch_all(query=query)

        if not records:
            raise ValueError(
                f"No content found for folio {folio} of manuscript {manuscript} of tradition {tradition}.")

        flattened_dictionary = self.contact_line_dictionary(
            [dict(record) for record in records])
        
        return flattened_dictionary
    
    async def get_folio_notes(self,
                              tradition: str,
                              manuscript: str,
                              folio: str,
                              user: str):
        """Retrieve all notes associated with a folio.
        """
        try:
            folio_id = await self.fetch_folio_id(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                user=user
            )
        except ValueError as e:
            raise ValueError(
                f"Folio {folio} not found for manuscript {manuscript} of tradition {tradition}.") from e
        query = self.format_query(f"""
            SELECT note, position_in_column, columns.position_in_folio
            FROM line_notes
            JOIN column_lines ON line_notes.line_id = column_lines.id
            JOIN columns ON column_lines.column_id = columns.id
            JOIN folios ON columns.folio_id = folios.id
            WHERE columns.folio_id = {folio_id}
        """)
        records = await self.database.fetch_all(query=query)
        records = [dict(record) for record in records]
        print(records)
        print(self.contact_line_dictionary(records, content_type="note"))
        if not records:
            raise ValueError(
                f"No notes found for folio {folio} of manuscript {manuscript} of tradition {tradition}.")
        return self.contact_line_dictionary(records, content_type="note")


class SCRIBESClient(SCRIBESCreateDelete, SCRIBESFetch, SCRIBESUpdate):
    """Mix-in class for all SCRIBES related data retrieval.
    """

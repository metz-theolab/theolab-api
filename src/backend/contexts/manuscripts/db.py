"""DB client to retrieve manuscript data within the QWB-API.
"""
import typing as t
from backend.tools.sql_client import SQLClient
from ..manuscripts.models import FOLLOWED_BY_MAPPER


MANUSCRIPT_TABLE = "manuscript_view"
MANUSCRIPT_COLUMN_TABLE = "manuscript_column"
MANUSCRIPT_LINE_TABLE = "manuscript_line"

class ManuscriptClient(SQLClient):
    """Manipulate textual data from the SQL database.
    """
    def check_manuscript_query(self, manuscript_name: str):
        """Build SQL query to check if a manuscript exists in the database.
        """
        return self.format_query(f"""
                SELECT EXISTS(SELECT 1 FROM {MANUSCRIPT_TABLE} WHERE manuscript = '{manuscript_name}') as exist
                """)

    def manuscript_query(self,
                         manuscript_name: str,
                         column: t.Optional[str] = None,
                         line: t.Optional[str] = None):
        """Build SQL query to retrieve manuscript data.

        Args:
            manuscript_name (str): Name of the manuscript to retrieve.
            column (t.Optional[str]): Column to retrieve. If set to None, all data is retrieved and
                line option is ignored.
            line (t.Optional[str]): Line to retrieve. If set to None, all column data is retrieved.
        """
        if line and not column:
            raise ValueError("Setting a value for line cannot be used without column option.")
        if column:
            if line:
                query = f"""
                    SELECT {MANUSCRIPT_TABLE}.manuscript, {MANUSCRIPT_TABLE}.reading, {MANUSCRIPT_TABLE}.followed_by, {MANUSCRIPT_TABLE}.sequence_in_line, {MANUSCRIPT_TABLE}.line
                    FROM {MANUSCRIPT_TABLE}
                    WHERE manuscript = '{manuscript_name}' AND {MANUSCRIPT_TABLE}.column = '{column}' AND {MANUSCRIPT_TABLE}.line = '{line}'
                    AND {MANUSCRIPT_TABLE}.language_id = 1
                    """
            else:
                query = f"""
                    SELECT {MANUSCRIPT_TABLE}.manuscript, {MANUSCRIPT_TABLE}.reading, {MANUSCRIPT_TABLE}.followed_by, {MANUSCRIPT_TABLE}.sequence_in_line, {MANUSCRIPT_TABLE}.line
                    FROM {MANUSCRIPT_TABLE}
                    WHERE {MANUSCRIPT_TABLE}.manuscript = '{manuscript_name}' AND {MANUSCRIPT_TABLE}.column = '{column}'
                    AND {MANUSCRIPT_TABLE}.language_id = 1
                    """
        else:
            query = f"""
                SELECT {MANUSCRIPT_TABLE}.manuscript, {MANUSCRIPT_TABLE}.reading, {MANUSCRIPT_TABLE}.followed_by, {MANUSCRIPT_TABLE}.sequence_in_line, {MANUSCRIPT_TABLE}.line
                FROM {MANUSCRIPT_TABLE}
                WHERE {MANUSCRIPT_TABLE}.manuscript = '{manuscript_name}'
                AND {MANUSCRIPT_TABLE}.language_id = 1
                """
        return self.format_query(query)
    
    def attribute_query(self, manuscript_name: str, attribute: str):
        """Given a manuscript, list all specified values of attribute available for this manuscript.
        """
        return self.format_query(f"""
                SELECT DISTINCT {MANUSCRIPT_TABLE}.{attribute} FROM {MANUSCRIPT_TABLE} WHERE {MANUSCRIPT_TABLE}.manuscript = '{manuscript_name}'
                """)
    
    def distinct_manuscript_query(self):
        """List all manuscripts available within the database.
        """
        return self.format_query("""
            SELECT DISTINCT manuscript FROM manuscript_view
            """)
    
    async def check_manuscript_exists(self, manuscript_name: str):
        """Check if a manuscript exists within a database.
        """
        query = self.check_manuscript_query(manuscript_name=manuscript_name)
        records = await self.database.fetch_all(query=query)
        results = [dict(record) for record in records]
        return results[0]["exist"] > 0

    async def get_manuscript(self,
                             manuscript_name: str,
                             column: t.Optional[str] = None,
                             line: t.Optional[str] = None):
        """Retrieve the content of a given manuscript.
        """
        query = self.manuscript_query(manuscript_name=manuscript_name,
                                      column=column, 
                                      line=line)
        records = await self.database.fetch_all(query=query)
        results = [dict(record) for record in records]
        return self.unpack_manuscript_data(results)

    def unpack_manuscript_data(self, records):
        """Unpack the manuscript data into a single string.
        """
        manuscript = ""
        for record in records:
            manuscript += record["reading"] + \
                FOLLOWED_BY_MAPPER[record["followed_by"]]
        return manuscript

    async def get_manuscript_attribute(self,
                                       manuscript_name: str,
                                       attribute: str):
        """List all columns available for a manuscript.
        """
        query = self.attribute_query(manuscript_name=manuscript_name, attribute=attribute)
        records = await self.database.fetch_all(query=query)
        results = [dict(record)[attribute] for record in records]
        return results
    
    async def get_distinct_manuscripts(self):
        """Get all distinct manuscripts.
        """
        query = self.distinct_manuscript_query()
        records = await self.database.fetch_all(query=query)
        results = [dict(record)["manuscript"] for record in records]
        return results
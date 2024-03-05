"""DB client to fetch textual data from the QWB API.
"""

from backend.tools.sql_client import SQLClient


class TextClient(SQLClient):
    """Manipulate textual data from the QWB API.
    """

    def build_parallel_query(self, tradition_name: str, chapter: str, verse: str):
        """Build SQL query to retrieve parallel data.
        """
        return self.format_query(f"""
                
                """)
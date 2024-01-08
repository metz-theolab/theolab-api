"""DB client to retrieve manuscript data within the QWB-API.
"""
from backend.tools.sql_client import SQLClient


class ManuscriptClient(SQLClient):
    """Manipulate textual data from the SQL database.
    """

    
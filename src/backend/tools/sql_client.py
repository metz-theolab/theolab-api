"""_summary_
"""
import typing as t

from databases import Database


class SQLClient:
    def __init__(self, uri: str, name: str) -> None:
        """
        Args:
            uri (str): The URI of the SQL database to connect to.
        """
        self.uri = f"{uri}/{name}"
        self.name = name
        self._database: t.Optional[Database] = None

    async def connect(self):
        """Connect the database."""
        self._database = Database(self.uri)
        await self._database.connect()

    async def disconnect(self):
        """Disconnect the database."""
        if self._database:
            await self._database.disconnect()

    @property
    def database(self) -> Database:
        """Return the database."""
        if not self._database:
            raise RuntimeError("Database is not yet connected.")
        return self._database

    @staticmethod
    def format_query(query: str):
        """Format an SQL query.
        """
        return " ".join(query.replace("\n", " ").strip().split())
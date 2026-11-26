from dataclasses import astuple, fields
from decimal import Decimal

from app.domain.entry import Entry

COLUMNS = ", ".join(field.name for field in fields(Entry))


class EntryRepository:
    def __init__(self, database):
        self.database = database

    def add(self, username, entry):
        values = [str(value) if isinstance(value, Decimal) else value for value in astuple(entry)]
        with self.database.connect() as connection:
            connection.execute(f"INSERT INTO entries (username, {COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [username, *values])

    def list(self, username):
        """All entries of the user, oldest first."""
        with self.database.connect() as connection:
            rows = connection.execute(f"SELECT {COLUMNS} FROM entries WHERE username = ? ORDER BY date, rowid", (username,)).fetchall()
        return [Entry(**{**dict(row), "total": Decimal(row["total"])}) for row in rows]

    def delete(self, username, ids):
        with self.database.connect() as connection:
            connection.executemany("DELETE FROM entries WHERE username = ? AND id = ?", [(username, entry_id) for entry_id in ids])

import os
import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    acc_dr INTEGER NOT NULL,
    acc_cr INTEGER NOT NULL,
    currency INTEGER NOT NULL,
    total TEXT NOT NULL,
    comment TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    accounts TEXT NOT NULL,
    currencies TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        """A connection for one transaction: committed on success, rolled back on error."""
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

import json

from app.domain.user import User


class UserRepository:
    def __init__(self, database):
        self.database = database

    def get(self, username):
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return None
        return User(row["username"], row["password_hash"], json.loads(row["accounts"]), json.loads(row["currencies"]))

    def save(self, user):
        with self.database.connect() as connection:
            connection.execute(
                "REPLACE INTO users (username, password_hash, accounts, currencies) VALUES (?, ?, ?, ?)",
                (user.username, user.password_hash, json.dumps(user.accounts), json.dumps(user.currencies)),
            )

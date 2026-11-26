import os
import tempfile
import unittest

from app import create_app
from tests.helpers import django_hash

AUTH = {"Authorization": "Bearer token"}
USER = {
    "password_hash": django_hash("pw"),
    "accounts": [{"id": 1, "name": "Cash", "group": "Assets", "depth": 0}, {"id": 2, "name": "Food", "group": "Expenses", "depth": 0}],
    "currencies": [{"id": 1, "name": "EUR", "selected": True}],
}
ENTRY = {"date": "2026-01-02", "acc_dr": "2", "acc_cr": "1", "currency": "1", "total": "12,50", "comment": "lunch"}


class ClientTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        app = create_app(
            {
                "SYNC_TOKEN": "token",
                "SECRET_KEY": "key",
                "DATABASE": os.path.join(tmp.name, "db.sqlite3"),
                "SESSION_COOKIE_SECURE": False,
                "LOGIN_DELAY": 0,
            }
        )
        self.client = app.test_client()
        for username in ("alice", "bob"):
            self.assertEqual(self.client.put(f"/api/users/{username}", json=USER, headers=AUTH).status_code, 204)

    def login(self, username="alice"):
        self.client.post("/login", data={"username": username, "password": "pw"})
        with self.client.session_transaction() as session:
            return session["csrf"]

    def pending(self, username="alice"):
        return self.client.get(f"/api/users/{username}/entries", headers=AUTH).get_json()

    def test_requires_auth(self):
        self.assertEqual(self.client.get("/").status_code, 302)
        self.assertEqual(self.client.post("/entries", data=ENTRY).status_code, 302)
        self.assertEqual(self.client.get("/api/users/alice/entries").status_code, 401)
        self.assertEqual(self.client.get("/api/users/alice/entries", headers={"Authorization": "Bearer nope"}).status_code, 401)
        for username, password in (("alice", "nope"), ("nobody", "pw")):
            self.client.post("/login", data={"username": username, "password": password})
            self.assertEqual(self.client.get("/").status_code, 302)

    def test_password_change_ends_session(self):
        self.login()
        self.assertEqual(self.client.get("/").status_code, 200)
        self.client.put("/api/users/alice", json={**USER, "password_hash": django_hash("new")}, headers=AUTH)
        self.assertEqual(self.client.get("/").status_code, 302)

    def test_users_are_separated(self):
        csrf = self.login("alice")
        self.client.post("/entries", data={**ENTRY, "csrf": csrf})
        (entry,) = self.pending("alice")
        self.assertEqual(self.pending("bob"), [])
        self.client.post("/api/users/bob/entries/delete", json={"ids": [entry["id"]]}, headers=AUTH)
        csrf = self.login("bob")
        self.assertNotIn(b"lunch", self.client.get("/").data)
        self.client.post(f"/entries/{entry['id']}/delete", data={"csrf": csrf})
        self.assertEqual(len(self.pending("alice")), 1)

    def test_requires_csrf(self):
        self.login()
        self.assertEqual(self.client.post("/entries", data=ENTRY).status_code, 400)
        self.assertEqual(self.pending(), [])

    def test_create_fetch_delete(self):
        csrf = self.login()
        self.client.post("/entries", data={**ENTRY, "csrf": csrf})
        (entry,) = self.pending()
        self.assertEqual((entry["acc_dr"], entry["acc_cr"], entry["total"]), (2, 1, "12.50"))
        self.assertIn(b"lunch", self.client.get("/").data)
        self.client.post("/api/users/alice/entries/delete", json={"ids": [entry["id"]]}, headers=AUTH)
        self.assertEqual(self.pending(), [])

    def test_rejects_invalid(self):
        csrf = self.login()
        for bad in ({"total": "abc"}, {"total": "NaN"}, {"total": "1.2345"}, {"total": "1e20"}, {"acc_dr": "99"}, {"date": "x"}):
            self.client.post("/entries", data={**ENTRY, **bad, "csrf": csrf})
        self.assertEqual(self.pending(), [])


if __name__ == "__main__":
    unittest.main()

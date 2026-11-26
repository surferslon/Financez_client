import os
import tempfile
import unittest
from decimal import Decimal

from app.domain.entry import InvalidEntry
from app.domain.user import User
from app.repositories.database import Database
from app.repositories.entries import EntryRepository
from app.repositories.users import UserRepository
from app.services.entries import EntryService
from app.services.users import UserService
from tests.helpers import django_hash


class ServiceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        database = Database(os.path.join(tmp.name, "db.sqlite3"))
        self.users = UserService(UserRepository(database))
        self.users.save(
            "alice", django_hash("pw"), [{"id": 1, "name": "Cash", "group": "Assets", "depth": 0}], [{"id": 1, "name": "EUR", "selected": True}]
        )
        self.alice = self.users.get("alice")
        self.entries = EntryService(EntryRepository(database))

    def test_authenticate(self):
        self.assertEqual(self.users.authenticate("alice", "pw"), self.alice)
        self.assertIsNone(self.users.authenticate("alice", "nope"))
        self.users.save("locked", "!unusable", [], [])
        self.assertIsNone(self.users.authenticate("locked", "!unusable"))

    def test_stored_entry_is_read_back_unchanged(self):
        entry = self.entries.add(self.alice, "2026-01-02", "1", "1", "1", " 12,50 ", " lunch ")
        self.assertEqual((entry.total, entry.comment), (Decimal("12.50"), "lunch"))
        self.assertEqual(self.entries.pending("alice"), [entry])
        self.entries.remove("alice", [entry.id])
        self.assertEqual(self.entries.pending("alice"), [])

    def test_account_tree(self):
        accounts = [
            {"id": i, "name": name, "group": group, "depth": depth}
            for i, (name, group, depth) in enumerate(
                [("Food", "Expenses", 0), ("Lunch", "Expenses", 1), ("Soup", "Expenses", 2), ("Coffee", "Expenses", 1), ("Cash", "Assets", 0)]
            )
        ]
        tree = User("alice", "", accounts, []).account_tree()

        def names(nodes):
            return [(node["name"], names(node["children"])) for node in nodes]

        self.assertEqual(
            {group: names(nodes) for group, nodes in tree.items()},
            {"Expenses": [("Food", [("Lunch", [("Soup", [])]), ("Coffee", [])])], "Assets": [("Cash", [])]},
        )

    def test_unknown_account(self):
        with self.assertRaises(InvalidEntry):
            self.entries.add(self.alice, "2026-01-02", "9", "1", "1", "1", "")
        self.assertEqual(self.entries.pending("alice"), [])

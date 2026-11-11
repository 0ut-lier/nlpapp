import tempfile
import unittest
from pathlib import Path

from PythonProject.mydb import Database


class DatabaseTests(unittest.TestCase):
    def test_register_and_authenticate(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Database(Path(folder) / "users.json")
            self.assertEqual(db.add_data("Test User", "TEST@example.com", "strongpass1"), 1)
            self.assertEqual(db.search("test@example.com", "strongpass1"), 1)
            self.assertEqual(db.search("test@example.com", "wrongpass"), 0)

    def test_duplicate_email_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Database(Path(folder) / "users.json")
            db.add_data("Test User", "test@example.com", "strongpass1")
            self.assertEqual(db.add_data("Other User", "TEST@example.com", "strongpass2"), 0)

    def test_rejects_invalid_registration(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Database(Path(folder) / "users.json")
            with self.assertRaises(ValueError):
                db.add_data("", "not-an-email", "short")


if __name__ == "__main__":
    unittest.main()

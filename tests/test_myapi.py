import unittest
from unittest.mock import Mock, patch

from PythonProject.myapi import API, APIError


class APITests(unittest.TestCase):
    def test_missing_key_is_reported(self):
        with self.assertRaisesRegex(APIError, "not configured"):
            API(api_key="").nlp_task("ner", "Ada Lovelace")

    def test_unknown_task_is_rejected(self):
        with self.assertRaises(ValueError):
            API(api_key="test").nlp_task("unknown", "hello")

    @patch("PythonProject.myapi.requests.post")
    def test_rate_limit_has_readable_error(self, post):
        response = Mock()
        response.status_code = 429
        response.ok = False
        post.return_value = response
        with self.assertRaisesRegex(APIError, "rate-limited"):
            API(api_key="test").nlp_task("ner", "Ada Lovelace")


if __name__ == "__main__":
    unittest.main()

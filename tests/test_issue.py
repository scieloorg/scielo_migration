import unittest
from unittest.mock import patch, PropertyMock

from scielo_classic_website.models.issue import Issue


class TestGetLicenseTextByLanguage(unittest.TestCase):

    def _make_issue(self, license_texts):
        record = {}
        issue = Issue(record)
        with patch.object(
            type(issue.issue_record), "license_texts",
            new_callable=PropertyMock, return_value=license_texts,
        ):
            return issue.get_license_text_by_language()

    def test_returns_texts_when_all_keys_present(self):
        license_texts = [
            {"language": "pt", "html": "<p>Licença</p>"},
            {"language": "en", "html": "<p>License</p>"},
        ]
        result = self._make_issue(license_texts)
        self.assertEqual(result, {
            "pt": "<p>Licença</p>",
            "en": "<p>License</p>",
        })

    def test_skips_item_missing_html_key(self):
        license_texts = [
            {"language": "pt"},
            {"language": "en", "html": "<p>License</p>"},
        ]
        result = self._make_issue(license_texts)
        self.assertEqual(result, {"en": "<p>License</p>"})

    def test_skips_item_missing_language_key(self):
        license_texts = [
            {"html": "<p>Licença</p>"},
            {"language": "en", "html": "<p>License</p>"},
        ]
        result = self._make_issue(license_texts)
        self.assertEqual(result, {"en": "<p>License</p>"})

    def test_skips_item_with_none_html(self):
        license_texts = [
            {"language": "pt", "html": None},
            {"language": "en", "html": "<p>License</p>"},
        ]
        result = self._make_issue(license_texts)
        self.assertEqual(result, {"en": "<p>License</p>"})

    def test_skips_item_with_none_language(self):
        license_texts = [
            {"language": None, "html": "<p>Licença</p>"},
            {"language": "en", "html": "<p>License</p>"},
        ]
        result = self._make_issue(license_texts)
        self.assertEqual(result, {"en": "<p>License</p>"})

    def test_returns_empty_dict_when_no_license_texts(self):
        result = self._make_issue([])
        self.assertEqual(result, {})

    def test_returns_empty_dict_when_all_items_incomplete(self):
        license_texts = [
            {"language": "pt"},
            {"html": "<p>License</p>"},
        ]
        result = self._make_issue(license_texts)
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()

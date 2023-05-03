from unittest import TestCase

from scielo_classic_website.attr_values import AttrValues


class TestAttrValues(TestCase):
    def test_isis_value(self):
        data = [
            {"isis": "oa", "sps": "research-article"},
        ]
        attr_values = AttrValues(data)
        expected = "oa"
        result = attr_values.get_isis_value("research-article")
        self.assertEqual(expected, result)

    def test_sps_value(self):
        data = [
            {"isis": "oa", "sps": "research-article"},
        ]
        attr_values = AttrValues(data)
        expected = "research-article"
        result = attr_values.get_sps_value("oa")
        self.assertEqual(expected, result)

    def test_isis_value_returns_none(self):
        data = [
            {"isis": "oa", "sps": "research-article"},
        ]
        attr_values = AttrValues(data)
        result = attr_values.get_isis_value("abstract")
        self.assertIsNone(result)

    def test_sps_value_returns_none(self):
        data = [
            {"isis": "oa", "sps": "research-article"},
        ]
        attr_values = AttrValues(data)
        result = attr_values.get_sps_value("xyz")
        self.assertIsNone(result)

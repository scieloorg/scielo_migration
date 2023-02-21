from unittest import TestCase

from scielo_classic_website.isisdb.raw_record import RawRecord


class RawRecordSimpleAttribSingleOccurenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"_": "xxxx"}
            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items("v700", {"_": ""})
        self.assertListEqual([{"": "xxxx"}], list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content("v700", {"_": ""}, True)
        self.assertEqual("xxxx", result)


class RawRecordSimpleAttribMultipleOccurrenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"_": "xxxx"},
                {"_": "yyyy"},
                {"_": "zzzz"},

            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items("v700", {"_": ""})
        self.assertListEqual(
            [{"": "xxxx"}, {"": "yyyy"}, {"": "zzzz"}], list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content("v700", {"_": ""}, False)
        self.assertEqual(["xxxx", "yyyy", "zzzz", ], result)


class RawRecordCompositeAttribSingleOccurenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"a": "xxxx", "b": "3"}
            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items("v700", {"a": "name", "b": "number"})
        self.assertListEqual([{"name": "xxxx", "number": "3"}], list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content(
            "v700", {"a": "name", "b": "number"}, True)
        self.assertEqual({"name": "xxxx", "number": "3"}, result)


class RawRecordCompositeAttribMultipleOccurrenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"a": "xxxx", "b": "3"},
                {"a": "yyyy", "b": "5"},
            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items(
            "v700", {"a": "name", "b": "number"})
        self.assertListEqual(
            [{"name": "xxxx", "number": "3"}, {"name": "yyyy", "number": "5"}],
            list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content(
            "v700", {"a": "name", "b": "number"}, False)
        self.assertEqual(
            [{"name": "xxxx", "number": "3"}, {"name": "yyyy", "number": "5"}],
            result)


class RawRecordAbsentSimpleAttribSingleOccurenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"_": "xxxx"}
            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items("v999", {"_": ""})
        self.assertListEqual([], list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content("v999", {"_": ""}, True)
        self.assertIsNone(result)


class RawRecordAbsentSimpleAttribMultipleOccurrenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"_": "xxxx"},
                {"_": "yyyy"},
                {"_": "zzzz"},

            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items("v999", {"_": ""})
        self.assertListEqual([], list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content("v999", {"_": ""}, False)
        self.assertEqual([], result)


class RawRecordAbsentCompositeAttribSingleOccurenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"a": "xxxx", "b": "3"}
            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items("v999", {"a": "name", "b": "number"})
        self.assertListEqual([], list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content(
            "v999", {"a": "name", "b": "number"}, True)
        self.assertIsNone(result)


class RawRecordAbsentCompositeAttribMultipleOccurrenceTest(TestCase):

    def setUp(self):
        record = {
            "v700": [
                {"a": "xxxx", "b": "3"},
                {"a": "yyyy", "b": "5"},
            ]
        }
        self.raw_record = RawRecord(record)

    def test_get_items(self):
        result = self.raw_record.get_items(
            "v999", {"a": "name", "b": "number"})
        self.assertListEqual([], list(result))

    def test_get_field_content(self):
        result = self.raw_record.get_field_content(
            "v999", {"a": "name", "b": "number"}, False)
        self.assertListEqual([], list(result))

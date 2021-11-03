from unittest import TestCase
from scielo_migration.iid2json import id2json3


class TestIsisIdToJson3(TestCase):

    def test_build_record(self):
        expected = {
            "10": [
                {"s": "surname", "n": "name"},
                {"s": "surname", "n": "name", "o": "xxx"},
            ],
            "12": [
                {"l": "en", "_": "title"},
                {"l": "es", "_": "título"},
            ],
        }
        data = [
            ["10", {"s": "surname", "n": "name"}],
            ["10", {"s": "surname", "n": "name", "o": "xxx"}],
            ["12", {"l": "en", "_": "title"}],
            ["12", {"l": "es", "_": "título"}],
        ]
        result = id2json3._build_record(data)
        self.assertEqual(expected, result)

    def test_parse_field_content(self):
        expected = {"s": "surname", "n": "name", "o": "xxx", "_": "bla"}
        data = "bla^ssurname^nname^oxxx"
        result = id2json3._parse_field_content(data)
        self.assertDictEqual(expected, result)

    def test_parse_field(self):
        expected = (
            "v9999", {"_": "bla", "s": "surname", "n": "name", "o": "xxx"})
        data = "!v9999!bla^ssurname^nname^oxxx"
        result = id2json3._parse_field(data)
        self.assertEqual(expected[0], result[0])
        self.assertDictEqual(expected[1], result[1])

    def test_get_id_file_rows(self):
        expected = """!ID 0000001
!v030!Acta Amaz.
!v031!49
!v032!3
!v035!0044-5967
!v036!20193
!v042!1""".splitlines()
        result = id2json3.get_id_file_rows("tests/fixtures/record.id")
        self.assertEqual(expected, list(result))

    def test_join_id_file_rows_and_return_records(self):
        rows = """!ID 0000001
!v030!Acta Amaz.
!v031!49
!v032!3
!v035!0044-5967
!v036!20193
!v042!1
!ID 0000002
!v004!v49n3
!v091!20190807
!v092!1231
!v093!20190807
!ID 0000003
!v004!v49n3
!v010!^1aff1 aff2^k0000-0002-3193-6659^nYardany^rND^sRAMOS-PASTRANA
!v010!^1aff1^nEric^rND^sCÓRDOBA-SUAREZ
!v010!^1aff2^nMarta^rND^sWOLFF""".splitlines()

        expected = [
            ("!v030!Acta Amaz.\n!v031!49\n!v032!3\n"
             "!v035!0044-5967\n!v036!20193\n!v042!1"),
            ("!v004!v49n3\n!v091!20190807\n!v092!1231\n"
                "!v093!20190807"),
            ("!v004!v49n3\n!v010!^1aff1 aff2^k0000-0002-3193-6659"
                "^nYardany^rND^sRAMOS-PASTRANA\n"
                "!v010!^1aff1^nEric^rND^sCÓRDOBA-SUAREZ\n"
                "!v010!^1aff2^nMarta^rND^sWOLFF"),
        ]
        result = id2json3.join_id_file_rows_and_return_records(rows)
        self.assertEqual(expected, list(result))

    def test_get_id_and_json_records(self):
        with open("tests/fixtures/hrecord.id") as fp:
            records = [fp.read()]
        expected_id = "S0044-59672019000300242"
        expected_records = [{
            "v004": [{"_": "v49n3"}],
            "v005": [{"_": "xxxx"}, {"_": "xxyz"}],
            "v010": [
                {"1": "aff1 aff2", "k": "0000-0002-3193-6659",
                 "n": "Yardany", "r": "ND", "s": "RAMOS-PASTRANA"},
                {"1": "aff2", "n": "Marta", "r": "ND", "s": "WOLFF"},
            ],
            "v882": [{"v": "49", "n": "3"}],
            "v880": [{"_": "S0044-59672019000300242"}],
            "v706": [{"_": "h"}],
        }]
        # `for` porque `id2json3.get_id_and_json_records` é um gerador
        for _id_and_records in id2json3.get_id_and_json_records(
                records, id2json3.article_id):
            _id, records = _id_and_records
            # executa apenas 1 vez, porque só há 1 registro
            self.assertEqual(expected_id, _id)
            self.assertEqual(expected_records, records)

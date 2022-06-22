from unittest import TestCase
from scielo_classic_website.isisdb import meta_record


class TestMetaRecord(TestCase):

    def setUp(self):
        record = {
            "v003": [{"_": "bla", "l": "en"}],
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
        }
        self.meta_record = meta_record.MetaRecord(record)

    def test_rec_type(self):
        expected = "h"
        result = self.meta_record.rec_type
        self.assertEqual(expected, result)

    def test_get_occ(self):
        expected = {
            "surname": "Lopes", "given-names": "M", "o": "xxx", "_": "bla"
        }
        subfields = {
            "s": "surname",
            "n": "given-names",
            "r": "role",
        }
        occ = {"s": "Lopes", "n": "M", "o": "xxx", "_": "bla"}
        result = self.meta_record._get_occ(occ, subfields)
        self.assertDictEqual(expected, result)

    def test_get_field_content_returns_v010(self):
        expected = [
            {"1": "aff1 aff2", "k": "0000-0002-3193-6659",
             "n": "Yardany", "r": "ND", "s": "RAMOS-PASTRANA"},
            {"1": "aff2", "n": "Marta", "r": "ND", "s": "WOLFF"},
        ]
        result = self.meta_record.get_field_content("v010")
        self.assertEqual(expected, result)

    def test_get_named_field_returns_authors(self):
        expected = {
            "authors": [
                {"1": "aff1 aff2", "k": "0000-0002-3193-6659",
                 "n": "Yardany", "r": "ND", "s": "RAMOS-PASTRANA"},
                {"1": "aff2", "n": "Marta", "r": "ND", "s": "WOLFF"},
            ]
        }
        result = self.meta_record.get_named_field("v010", "authors")
        self.assertEqual(expected, result)

    def test_get_named_field_returns_authors_and_renamed_subfields(self):
        expected = {
            "authors": [
                {"aff_rid": "aff1 aff2", "orcid": "0000-0002-3193-6659",
                 "given-names": "Yardany", "role": "ND",
                 "surname": "RAMOS-PASTRANA"},
                {"aff_rid": "aff2", "given-names": "Marta", "role": "ND",
                 "surname": "WOLFF"},
            ]
        }
        subfields = {
            "s": "surname",
            "n": "given-names",
            "r": "role",
            "k": "orcid",
            "1": "aff_rid",
        }
        result = self.meta_record.get_named_field(
            "v010", "authors", subfields)
        self.assertEqual(expected, result)

    def test_get_named_field_returns_v882_with_single(self):
        expected = {"v882": {"v": "49", "n": "3"}}
        result = self.meta_record.get_named_field(
            "v882", single=True)
        self.assertEqual(expected, result)

    def test_get_named_field_returns_v882_with_single_as_False(self):
        expected = {"v882": [{"v": "49", "n": "3"}]}
        result = self.meta_record.get_named_field(
            "v882", single=False)
        self.assertEqual(expected, result)

    def test_get_named_field_returns_v004_with_simple_as_True(self):
        expected = {"v004": ["v49n3"]}
        result = self.meta_record.get_named_field(
            "v004", simple=True)
        self.assertEqual(expected, result)

    def test_get_named_field_returns_v004_with_simple_as_False(self):
        expected = {"v004": [{"_": "v49n3"}]}
        result = self.meta_record.get_named_field(
            "v004", simple=False)
        self.assertEqual(expected, result)

    def test_get_named_field_returns_v004_with_simple_as_True_and_single_as_True(self):
        expected = {"v004": "v49n3"}
        result = self.meta_record.get_named_field(
            "v004", single=True, simple=True)
        self.assertEqual(expected, result)

    def test_get_named_field_returns_v005_with_simple_as_True(self):
        expected = {"v005": ["xxxx", "xxyz"]}
        result = self.meta_record.get_named_field(
            "v005", simple=True)
        self.assertEqual(expected, result)

    def test_get_record_subset_as_dict(self):
        """
        Testa que ao executar `get_record_subset_as_dict` com

        data_dict = {
            "v010": {
                "field_name": "autores",
                "subfields": {"n": "nome"},
            },
            "v005": {
                "field_name": "codigos",
                "simple": True,
            },
            "v706": {
                "field_name": "rec_tp",
                "simple": True,
                "single": True,
            },
            "v880": {
                "field_name": "PID",
            },
        }
        retorna somente as tags indicadas no `data_dict` e retorna os dados
        de acordo com os parâmetros indicados no `data_dict`, ou seja,
        `field_name`, `subfields`, `simple`, `single`
        """
        data_dict = {
            "v003": {
                "field_name": "resumo",
                "subfields": {"_": "texto", "l": "idioma"},
                "is_multi_val": True,
            },
            "v010": {
                "field_name": "autores",
                "subfields": {"n": "nome"},
                "is_multi_val": True,
            },
            "v005": {
                "field_name": "codigos",
                "is_multi_val": True,
            },
            "v706": {
                "field_name": "rec_tp",
            },
            "v880": {
                "field_name": "PID",
                "is_multi_val": True,
                "subfields": {"_": "_"},
            },
        }
        expected = {
            "resumo": [{"texto": "bla", "idioma": "en"}],
            "autores": [
                {"1": "aff1 aff2", "k": "0000-0002-3193-6659",
                 "nome": "Yardany", "r": "ND", "s": "RAMOS-PASTRANA"},
                {"1": "aff2", "nome": "Marta", "r": "ND", "s": "WOLFF"},
            ],
            "codigos": ["xxxx", "xxyz"],
            "rec_tp": "h",
            "PID": [{"_": "S0044-59672019000300242"}],
        }
        result = self.meta_record.get_record_subset_as_dict(data_dict)
        self.assertEqual(expected, result)

    def test_get_full_record_as_dict_returns_autores_and_nome(self):
        """
        Testa que ao executar `get_full_record_as_dict` com o valor para
        `data_dict` igual a
            ```
            {
                "v010": {
                    "field_name": "autores",
                    "subfields": {"n": "nome"},
                }
            }
            ```
        retorna o registro completo, retornando no lugar de `v010` o valor
        `autores`, no lugar de `n`, o valor `nome`.
        """
        data_dict = {
            "v010": {
                "field_name": "autores",
                "subfields": {"n": "nome"},
                "is_multi_val": True,
            },

        }
        expected = {
            "v003": [{"_": "bla", "l": "en"}],
            "v004": [{"_": "v49n3"}],
            "v005": [{"_": "xxxx"}, {"_": "xxyz"}],
            "autores": [
                {"1": "aff1 aff2", "k": "0000-0002-3193-6659",
                 "nome": "Yardany", "r": "ND", "s": "RAMOS-PASTRANA"},
                {"1": "aff2", "nome": "Marta", "r": "ND", "s": "WOLFF"},
            ],
            "v882": [{"v": "49", "n": "3"}],
            "v880": [{"_": "S0044-59672019000300242"}],
            "v706": [{"_": "h"}],
        }
        result = self.meta_record.get_full_record_as_dict(data_dict)
        self.assertEqual(expected, result)

    def test_get_full_record_as_dict_uses_class_data_dict(self):
        """
        Testa que ao executar `get_full_record_as_dict` com o valor para
        `self.meta_record._data_dictionary` igual a
            ```
            {
                "v010": {
                    "field_name": "autores",
                    "subfields": {"n": "nome"},
                }
            }
            ```
        retorna o registro completo, retornando no lugar de `v010` o valor
        `autores`, no lugar de `n`, o valor `nome`.
        """
        self.meta_record._data_dictionary = {
            "v010": {
                "field_name": "authors",
                "subfields": {
                    "n": "name", "s": "surname", "1": "affs", "k": "orcid",
                },
                "is_multi_val": True,
            }
        }
        expected = {
            "v003": [{"_": "bla", "l": "en"}],
            "v004": [{"_": "v49n3"}],
            "v005": [{"_": "xxxx"}, {"_": "xxyz"}],
            "authors": [
                {"affs": "aff1 aff2", "orcid": "0000-0002-3193-6659",
                 "name": "Yardany", "r": "ND", "surname": "RAMOS-PASTRANA"},
                {"affs": "aff2", "name": "Marta", "r": "ND", "surname": "WOLFF"},
            ],
            "v882": [{"v": "49", "n": "3"}],
            "v880": [{"_": "S0044-59672019000300242"}],
            "v706": [{"_": "h"}],
        }
        result = self.meta_record.get_full_record_as_dict(None)
        self.assertEqual(expected, result)

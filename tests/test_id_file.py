import datetime
import os
import tempfile
from unittest import TestCase

from scielo_classic_website.iid2json import id2json3
from scielo_classic_website.iid2json.id_file import (
    ClassicIdFile,
    filter_date,
    get_p_records_file_path,
    normalize_date,
)

TITLE_ID = """!ID 0000001
!v100!Revista A
!v400!0001-0001
!v940!20100101
!v941!20230510
!ID 0000002
!v100!Revista B
!v400!0002-0002
!v940!20120101
!v941!20240115
!ID 0000003
!v100!Revista C
!v400!0003-0003
"""

ISSUE_ID = """!ID 0000001
!v030!Acta
!v035!0044-5967
!v036!20193
!v091!20191001
!ID 0000002
!v030!Acta
!v035!0044-5967
!v036!20201
!v091!20200301
"""

ARTIGO_ID = """!ID 0000001
!v706!i
!v035!0044-5967
!v036!20193
!v091!20191001
!ID 0000002
!v706!o
!v880!S0044-59672019000300001
!v091!20191005
!ID 0000003
!v706!h
!v880!S0044-59672019000300001
!v065!20190900
!v012!Titulo com
quebra de linha^len
!ID 0000004
!v706!p
!v880!S0044-59672019000300001
!v704!paragrafo
!ID 0000005
!v706!o
!v880!S0044-59672019000300002
!v091!20200110
!ID 0000006
!v706!h
!v880!S0044-59672019000300002
"""


class IdFileTestBase(TestCase):
    content = ""
    db_type = None

    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".id")
        with os.fdopen(fd, "w", encoding="iso-8859-1") as fp:
            fp.write(self.content)
        self.id_file = ClassicIdFile(self.db_type, self.path)

    def tearDown(self):
        os.remove(self.path)

    def assert_compatible_with_id2json3(self):
        expected = list(id2json3.pids_and_their_records(self.path, self.id_file.db_type))
        self.assertEqual(expected, list(self.id_file.pids_and_records()))


class TestTitleIdFile(IdFileTestBase):
    content = TITLE_ID
    db_type = "journal"

    def test_compatible_with_id2json3(self):
        self.assert_compatible_with_id2json3()

    def test_pids_and_dates(self):
        self.assertEqual(
            [("0001-0001", "20230510"), ("0002-0002", "20240115"), ("0003-0003", None)],
            list(self.id_file.pids_and_dates()),
        )

    def test_creation_date(self):
        self.assertEqual(
            ["20100101", "20120101", None],
            [d for _, d in self.id_file.pids_and_dates(date_field="creation")],
        )

    def test_filter_since(self):
        self.assertEqual(["0002-0002"], list(self.id_file.pids(since="20240101")))

    def test_filter_until(self):
        self.assertEqual(["0001-0001"], list(self.id_file.pids(until="20230531")))

    def test_filter_since_includes_equal_date(self):
        # since: data igual ou maior
        self.assertEqual(["0002-0002"], list(self.id_file.pids(since="20240115")))
        self.assertEqual([], list(self.id_file.pids(since="20240116")))
        self.assertEqual(
            ["0001-0001", "0002-0002"], list(self.id_file.pids(since="20230510"))
        )

    def test_filter_until_includes_equal_date(self):
        # until: data igual ou menor
        self.assertEqual(["0001-0001"], list(self.id_file.pids(until="20230510")))
        self.assertEqual([], list(self.id_file.pids(until="20230509")))
        self.assertEqual(
            ["0001-0001", "0002-0002"], list(self.id_file.pids(until="20240115"))
        )

    def test_filter_since_and_until_same_day(self):
        self.assertEqual(
            ["0001-0001"],
            list(self.id_file.pids(since="20230510", until="20230510")),
        )
        self.assertEqual(
            ["0002-0002"],
            list(self.id_file.pids(
                since=datetime.date(2024, 1, 15), until=datetime.date(2024, 1, 15)
            )),
        )

    def test_filter_include_undated(self):
        self.assertEqual(
            ["0002-0002", "0003-0003"],
            list(self.id_file.pids(since=datetime.date(2024, 1, 1), include_undated=True)),
        )

    def test_get_and_data(self):
        item = self.id_file.get("0002-0002")
        self.assertEqual("Revista B", item.data["v100"][0]["_"])
        self.assertEqual("journal", item.kind)
        self.assertEqual(datetime.date(2024, 1, 15), item.date_as_date)
        self.assertIsNone(self.id_file.get("9999-9999"))

    def test_get_with_index(self):
        index = self.id_file.build_index()
        self.assertEqual(3, len(index))
        item = self.id_file.get("0003-0003")
        self.assertEqual("Revista C", item.data["v100"][0]["_"])
        self.assertEqual(1, len(item.records))


class TestIssueIdFile(IdFileTestBase):
    content = ISSUE_ID
    db_type = "issue"

    def test_compatible_with_id2json3(self):
        self.assert_compatible_with_id2json3()

    def test_pids_and_dates(self):
        self.assertEqual(
            [("0044-596720190003", "20191001"), ("0044-596720200001", "20200301")],
            list(self.id_file.pids_and_dates()),
        )

    def test_filter_pids(self):
        self.assertEqual(
            ["0044-596720200001"], list(self.id_file.pids(pids=["0044-596720200001"]))
        )


class TestArtigoIdFile(IdFileTestBase):
    content = ARTIGO_ID
    db_type = "artigo"

    def test_compatible_with_id2json3(self):
        self.assert_compatible_with_id2json3()

    def test_kinds_and_dates(self):
        result = [(i.pid, i.kind, i.date) for i in self.id_file.items()]
        self.assertEqual(
            [
                ("0044-596720190003", "issue", "20191001"),
                ("S0044-59672019000300001", "document", "20191005"),
                ("S0044-59672019000300002", "document", "20200110"),
            ],
            result,
        )

    def test_filter_documents_by_date(self):
        self.assertEqual(
            ["S0044-59672019000300002"],
            list(self.id_file.pids(kind="document", since="20200101")),
        )

    def test_publication_date(self):
        item = self.id_file.get("S0044-59672019000300001", date_field="publication")
        self.assertEqual("20190900", item.date)
        self.assertIsNone(item.date_as_date)

    def test_records_are_lazy_and_complete(self):
        item = self.id_file.get("S0044-59672019000300001")
        self.assertIsNone(item._records)
        self.assertIsNone(item._main_records)
        self.assertEqual(3, len(item.records))
        self.assertIs(item.records, item.records)
        self.assertEqual(item.main_records, item.records)
        self.assertEqual("0044-596720190003", item.issue_pid)
        self.assertEqual(
            {"_": "Titulo com quebra de linha", "l": "en"}, item.records[1]["v012"][0]
        )

    def test_get_with_index(self):
        self.id_file.build_index()
        item = self.id_file.get("S0044-59672019000300002")
        self.assertEqual(2, len(item.records))


class TestNormalizeDate(TestCase):
    def test_values(self):
        self.assertEqual("20240315", normalize_date("2024-03-15"))
        self.assertEqual("20240000", normalize_date("2024"))
        self.assertEqual("20249999", normalize_date("2024", "9"))
        self.assertEqual("20240315", normalize_date(datetime.date(2024, 3, 15)))
        self.assertIsNone(normalize_date(None))
        self.assertIsNone(normalize_date(""))

    def test_filter_date(self):
        self.assertEqual("20240315", filter_date("20240315"))
        self.assertEqual("20240315", filter_date(datetime.date(2024, 3, 15)))
        self.assertEqual("20240315", filter_date(datetime.datetime(2024, 3, 15, 10, 5)))
        self.assertIsNone(filter_date(None))

    def test_invalid_db_type(self):
        with self.assertRaises(ValueError):
            ClassicIdFile("xxx", "x.id")


ARTIGO_WITH_REPEATED_I_ID = """!ID 0000001
!v706!i
!v035!0044-5967
!v036!20193
!ID 0000002
!v706!o
!v880!S0044-59672019000300001
!v091!20191005
!ID 0000003
!v706!h
!v880!S0044-59672019000300001
!ID 0000004
!v706!i
!v035!0044-5967
!v036!20193
!ID 0000005
!v706!p
!v880!S0044-59672019000300001
!ID 0000006
!v706!i
!v035!0044-5967
!v036!20194
!ID 0000007
!v706!c
!v880!S0044-59672019000300001
!ID 0000008
!v706!o
!v880!S0044-59672019000400001
!v091!20191201
"""


class TestArtigoIdFileWithIRecordInsideDocument(IdFileTestBase):
    content = ARTIGO_WITH_REPEATED_I_ID
    db_type = "artigo"

    def test_i_record_does_not_split_document(self):
        result = [(i.pid, i.kind, len(i.records)) for i in self.id_file.items()]
        self.assertEqual(
            [
                ("0044-596720190003", "issue", 1),
                ("S0044-59672019000300001", "document", 4),
                ("0044-596720190003", "issue", 1),
                ("0044-596720190004", "issue", 1),
            ],
            result,
        )
        # só registro "o" (sem "h"): fica separado, em broken_batches()
        self.assertEqual(
            [("S0044-59672019000400001", "broken", 1)],
            [(i.pid, i.kind, len(i.records)) for i in self.id_file.broken_batches()],
        )

    def test_document_records_do_not_include_i(self):
        item = self.id_file.get("S0044-59672019000300001")
        self.assertEqual(
            ["o", "h", "p", "c"], [r["v706"][0]["_"] for r in item.records]
        )
        self.assertEqual("20191005", item.date)

    def test_get_with_index(self):
        self.id_file.build_index()
        # pids únicos dos itens bons (o lote quebrado S...400001 não entra)
        self.assertEqual(3, len(self.id_file.index))
        self.assertIsNone(self.id_file.get("S0044-59672019000400001"))
        self.assertEqual(4, len(self.id_file.get("S0044-59672019000300001").records))
        self.assertEqual("issue", self.id_file.get("0044-596720190004").kind)


class TestArtigoExternalPRecords(TestCase):
    MAIN = """!ID 0000001
!v706!o
!v880!S0044-59672019000300001
!v091!20191005
!ID 0000002
!v706!h
!v880!S0044-59672019000300001
!ID 0000003
!v706!o
!v880!S0044-59672019000300002
!v091!20191005
!ID 0000004
!v706!h
!v880!S0044-59672019000300002
!ID 0000005
!v706!p
!v880!S0044-59672019000300002
!v704!paragrafo interno
"""
    P_FILE = """!ID 0000001
!v706!p
!v880!S0044-59672019000300001
!v704!paragrafo 1
!ID 0000002
!v706!p
!v880!S0044-59672019000300001
!v704!paragrafo 2
"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bases_work = os.path.join(self.tmp.name, "bases-work")
        self.bases = os.path.join(self.tmp.name, "bases")
        self.main_path = os.path.join(self.tmp.name, "acron.id")
        with open(self.main_path, "w", encoding="iso-8859-1") as fp:
            fp.write(self.MAIN)
        p_dir = os.path.join(self.bases, "artigo", "p", "0044-5967", "2019", "0003")
        os.makedirs(p_dir)
        self.p_path = os.path.join(p_dir, "00001.id")
        with open(self.p_path, "w", encoding="iso-8859-1") as fp:
            fp.write(self.P_FILE)

    def tearDown(self):
        self.tmp.cleanup()

    def test_get_p_records_file_path(self):
        self.assertEqual(
            self.p_path,
            get_p_records_file_path(
                "S0044-59672019000300001", [self.bases_work, self.bases]
            ),
        )
        self.assertIsNone(
            get_p_records_file_path("S0044-59672019000300002", [self.bases])
        )

    def test_records_include_external_p_records(self):
        id_file = ClassicIdFile(
            "artigo", self.main_path, p_records_base_paths=[self.bases_work, self.bases]
        )
        item = id_file.get("S0044-59672019000300001")
        self.assertEqual(
            ["o", "h", "p", "p"], [r["v706"][0]["_"] for r in item.records]
        )
        self.assertEqual(2, len(item.main_records))
        self.assertEqual(
            ["paragrafo 1", "paragrafo 2"],
            [r["v704"][0]["_"] for r in item.p_records],
        )
        self.assertEqual(self.p_path, item.external_p_records_path)

    def test_main_p_records_take_precedence(self):
        id_file = ClassicIdFile("artigo", self.main_path, p_records_base_paths=self.bases)
        item = id_file.get("S0044-59672019000300002")
        self.assertIsNone(item.external_p_records_path)
        self.assertEqual(
            ["paragrafo interno"], [r["v704"][0]["_"] for r in item.p_records]
        )

    def test_without_base_paths_external_p_records_are_ignored(self):
        item = ClassicIdFile("artigo", self.main_path).get("S0044-59672019000300001")
        self.assertEqual(["o", "h"], [r["v706"][0]["_"] for r in item.records])

    def test_records_keep_main_records_before_external_p_records(self):
        id_file = ClassicIdFile("artigo", self.main_path, p_records_base_paths=self.bases)
        item = id_file.get("S0044-59672019000300001")
        self.assertEqual(item.main_records, item.records[:2])
        self.assertEqual(item.external_p_records, item.records[2:])

    def test_records_are_cached_and_external_file_is_read_once(self):
        id_file = ClassicIdFile("artigo", self.main_path, p_records_base_paths=self.bases)
        item = id_file.get("S0044-59672019000300001")
        records = item.records
        os.remove(self.p_path)
        self.assertIs(records, item.records)
        self.assertEqual(4, len(item.records))

    def test_main_p_records_are_not_duplicated(self):
        id_file = ClassicIdFile("artigo", self.main_path, p_records_base_paths=self.bases)
        item = id_file.get("S0044-59672019000300002")
        self.assertTrue(item.has_main_p_records)
        self.assertEqual(item.main_records, item.records)
        self.assertEqual(["o", "h", "p"], [r["v706"][0]["_"] for r in item.records])

    def test_records_without_external_file_are_main_records(self):
        os.remove(self.p_path)
        id_file = ClassicIdFile("artigo", self.main_path, p_records_base_paths=self.bases)
        item = id_file.get("S0044-59672019000300001")
        self.assertIsNone(item.external_p_records_path)
        self.assertEqual([], item.external_p_records)
        self.assertEqual(item.main_records, item.records)

    def test_issue_record_in_artigo_does_not_read_external_p_records(self):
        path = os.path.join(self.tmp.name, "with_i.id")
        with open(path, "w", encoding="iso-8859-1") as fp:
            fp.write(ARTIGO_ID)
        p_dir = os.path.join(self.bases, "artigo", "p", "0044-5967", "2019", "0003")
        with open(os.path.join(p_dir, "00000.id"), "w", encoding="iso-8859-1") as fp:
            fp.write(self.P_FILE)
        id_file = ClassicIdFile("artigo", path, p_records_base_paths=self.bases)
        issue = id_file.get("0044-596720190003")
        self.assertEqual("issue", issue.kind)
        self.assertIsNone(issue.external_p_records_path)
        self.assertEqual(["i"], [r["v706"][0]["_"] for r in issue.records])

    def test_title_and_issue_records_are_main_records(self):
        for db_type, content in (("title", TITLE_ID), ("issue", ISSUE_ID)):
            with self.subTest(db_type=db_type):
                path = os.path.join(self.tmp.name, f"{db_type}.id")
                with open(path, "w", encoding="iso-8859-1") as fp:
                    fp.write(content)
                id_file = ClassicIdFile(db_type, path, p_records_base_paths=self.bases)
                item = next(iter(id_file.items()))
                self.assertEqual(item.main_records, item.records)
                self.assertIs(item.records[0], item.data)


class TestItemMfn(IdFileTestBase):
    content = ARTIGO_ID
    db_type = "artigo"

    def test_mfn_of_items(self):
        # registro i (mfn 1); documento 1 com o, h, p (mfn 2..4)
        items = list(self.id_file.items())
        self.assertEqual((1, 1), (items[0].mfn, items[0].last_mfn))
        self.assertEqual((2, 4), (items[1].mfn, items[1].last_mfn))


class TestArtigoRealFileQuirks(IdFileTestBase):
    # baseado em mioc.id: registros sem v706 e PID repetido (o solto e depois completo)
    content = """!ID 0000001
!v706!o
!v880!S0074-02761997000200008
!v091!19981014
!ID 0000002
!v880!S
!v936!^i0074-0276^y2007^o50
!ID 0000003
!v880!S
!v936!^i0074-0276^y2007^o50
!ID 0000004
!v706!i
!v035!0074-0276
!v036!19972
!ID 0000005
!v706!o
!v880!S0074-02761997000200008
!v091!19981020
!ID 0000006
!v706!h
!v880!S0074-02761997000200008
!ID 0000007
!v706!f
!v880!S0074-02761997000200008
"""
    db_type = "artigo"

    def test_records_without_v706_are_ignored(self):
        result = [(i.pid, i.kind, len(i.records)) for i in self.id_file.items()]
        self.assertEqual(
            [
                ("0074-027619970002", "issue", 1),
                ("S0074-02761997000200008", "document", 3),
            ],
            result,
        )
        # "o" solto, sem "h"
        self.assertEqual(
            [("S0074-02761997000200008", "broken", 1)],
            [(i.pid, i.kind, len(i.records)) for i in self.id_file.broken_batches()],
        )

    def test_get_returns_last_occurrence(self):
        self.assertEqual(3, len(self.id_file.get("S0074-02761997000200008").records))
        self.id_file.build_index()
        item = self.id_file.get("S0074-02761997000200008")
        self.assertEqual(3, len(item.records))
        self.assertEqual("19981020", item.date)


class TestArtigoDocumentRequiresOAndHRecords(IdFileTestBase):
    content = """!ID 0000001
!v706!o
!v880!S0044-59672019000300001
!v091!20191005
!ID 0000002
!v706!h
!v880!S0044-59672019000300001
!ID 0000003
!v706!f
!v880!S0044-59672019000300001
!ID 0000004
!v706!o
!v880!S0044-59672019000300002
!v091!20191005
!ID 0000005
!v706!f
!v880!S0044-59672019000300002
!ID 0000006
!v706!h
!v880!S0044-59672019000300003
!ID 0000007
!v706!f
!v880!S0044-59672019000300003
!ID 0000008
!v706!o
!v880!S0044-59672019000300004
!v091!20191005
!ID 0000009
!v706!h
!v880!S0044-59672019000300004
"""
    db_type = "artigo"

    def test_items_returns_only_documents(self):
        result = [(i.pid, i.kind, i.record_types) for i in self.id_file.items()]
        self.assertEqual(
            [
                ("S0044-59672019000300001", "document", ("o", "h", "f")),
                # "o" e "h" bastam (f, l, p, c... não são verificados)
                ("S0044-59672019000300004", "document", ("o", "h")),
            ],
            result,
        )

    def test_broken_batches(self):
        result = [
            (i.pid, i.kind, i.record_types) for i in self.id_file.broken_batches()
        ]
        self.assertEqual(
            [
                # sem "h"
                ("S0044-59672019000300002", "broken", ("o", "f")),
                # sem "o"
                ("S0044-59672019000300003", "broken", ("h", "f")),
            ],
            result,
        )

    def test_get_ignores_broken_batches(self):
        self.assertIsNone(self.id_file.get("S0044-59672019000300002"))
        self.id_file.build_index()
        self.assertNotIn("S0044-59672019000300002", self.id_file.index)
        self.assertIsNone(self.id_file.get("S0044-59672019000300002"))

    def test_filter_by_kind_document(self):
        self.assertEqual(
            ["S0044-59672019000300001", "S0044-59672019000300004"],
            list(self.id_file.pids(kind="document")),
        )

    def test_broken_batch_does_not_read_external_p_records(self):
        # arquivos p externos existem para o documento válido (00001) e para
        # o lote quebrado "o", "f" (00002); só o documento deve usá-los
        with tempfile.TemporaryDirectory() as bases:
            p_dir = os.path.join(bases, "artigo", "p", "0044-5967", "2019", "0003")
            os.makedirs(p_dir)
            for number in ("00001", "00002"):
                with open(os.path.join(p_dir, f"{number}.id"), "w") as fp:
                    fp.write(
                        f"!ID 0000001\n!v706!p\n"
                        f"!v880!S0044-596720190003{number}\n!v704!paragrafo\n"
                    )
            id_file = ClassicIdFile(
                "artigo", self.path, p_records_base_paths=[bases]
            )

            document = id_file.get("S0044-59672019000300001")
            self.assertEqual("document", document.kind)
            self.assertEqual(
                os.path.join(p_dir, "00001.id"), document.external_p_records_path
            )
            self.assertEqual(1, len(document.p_records))

            (broken,) = [
                b for b in id_file.broken_batches()
                if b.pid == "S0044-59672019000300002"
            ]
            self.assertEqual("broken", broken.kind)
            self.assertEqual("o", broken.record_type)
            self.assertIsNone(broken.external_p_records_path)
            self.assertEqual([], broken.external_p_records)
            self.assertEqual([], broken.p_records)


class TestArtigoBatchesFollowRecordTypesOrder(IdFileTestBase):
    # mesmo PID em todos os registros: só a ordem dos tipos separa os lotes
    content = """!ID 0000001
!v706!o
!v880!S0044-59672019000300001
!v091!20191005
!ID 0000002
!v706!h
!v880!S0044-59672019000300001
!ID 0000003
!v706!f
!v880!S0044-59672019000300001
!ID 0000004
!v706!c
!v880!S0044-5967201900030000100001
!ID 0000005
!v706!c
!v880!S0044-5967201900030000100002
!ID 0000006
!v706!h
!v880!S0044-59672019000300001
!ID 0000007
!v706!f
!v880!S0044-59672019000300001
!ID 0000008
!v706!o
!v880!S0044-59672019000300001
!v091!20191010
!ID 0000009
!v706!o
!v880!S0044-59672019000300001
!v091!20191011
!ID 0000010
!v706!h
!v880!S0044-59672019000300001
!ID 0000011
!v706!h
!v880!S0044-59672019000300001
"""
    db_type = "artigo"

    def test_batches(self):
        result = sorted(
            (i.mfn, i.last_mfn, i.kind, "".join(i.record_types))
            for i in list(self.id_file.items()) + list(self.id_file.broken_batches())
        )
        self.assertEqual(
            [
                (1, 5, "document", "ohfcc"),
                # "h" depois de "c": a ordem se inverte
                (6, 7, "broken", "hf"),
                # "o" depois de "f"
                (8, 8, "broken", "o"),
                # "o" depois de "o"
                (9, 10, "document", "oh"),
                # "h" não se repete
                (11, 11, "broken", "h"),
            ],
            result,
        )

    def test_broken_batches(self):
        self.assertEqual(
            [(6, "hf"), (8, "o"), (11, "h")],
            [
                (i.mfn, "".join(i.record_types))
                for i in self.id_file.broken_batches()
            ],
        )

    def test_items_does_not_return_broken_batches(self):
        self.assertEqual(
            [(1, "document"), (9, "document")],
            [(i.mfn, i.kind) for i in self.id_file.items()],
        )

    def test_get_returns_last_good_occurrence(self):
        # o lote quebrado "h" (MFN 11) vem depois, mas não substitui o documento
        self.assertEqual(9, self.id_file.get("S0044-59672019000300001").mfn)
        self.id_file.build_index()
        self.assertEqual(9, self.id_file.get("S0044-59672019000300001").mfn)

    def _full_reads(self):
        """Conta as leituras do arquivo a partir do início"""
        calls = []
        original = self.id_file.iter_raw_records

        def iter_raw_records(start=0):
            calls.append(start)
            return original(start)

        self.id_file.iter_raw_records = iter_raw_records
        return calls

    def test_broken_batches_after_items_does_not_read_whole_file_again(self):
        list(self.id_file.items())
        calls = self._full_reads()
        self.assertEqual(
            [(6, "hf"), (8, "o"), (11, "h")],
            [(i.mfn, "".join(i.record_types)) for i in self.id_file.broken_batches()],
        )
        # só leituras a partir das posições dos lotes, nenhuma do início
        self.assertNotIn(0, calls)
        self.assertEqual(3, len(calls))

    def test_broken_batches_without_previous_reading_reads_whole_file(self):
        calls = self._full_reads()
        self.assertEqual(3, len(list(self.id_file.broken_batches())))
        self.assertEqual([0], calls)
        # a leitura completa registra as posições: a próxima não relê
        calls.clear()
        self.assertEqual(3, len(list(self.id_file.broken_batches())))
        self.assertNotIn(0, calls)

    def test_interrupted_reading_does_not_register_positions(self):
        for item in self.id_file.items():
            break
        self.assertIsNone(self.id_file._known_broken_offsets())

    def test_positions_are_discarded_when_file_changes(self):
        list(self.id_file.items())
        with open(self.path, "a", encoding="iso-8859-1") as fp:
            fp.write("!ID 0000012\n!v706!o\n!v880!S0044-59672019000300009\n!v091!20191012\n")
        os.utime(self.path, ns=(0, 10**9))
        self.assertIsNone(self.id_file._known_broken_offsets())
        self.assertEqual(
            [6, 8, 11, 12], [i.mfn for i in self.id_file.broken_batches()]
        )

    def test_broken_batches_does_not_accept_filters(self):
        with self.assertRaises(TypeError):
            list(self.id_file.broken_batches(since="20191010"))

    def test_broken_batches_are_not_documents(self):
        self.assertEqual([1, 9], [i.mfn for i in self.id_file.items(kind="document")])


class TestLineBreaksInsideFieldContent(IdFileTestBase):
    content = (
        "!ID 0000001\n"
        "!v706!o\n"
        "!v880!S0044-59672019000300001\n"
        "!v091!20191005\n"
        "!ID 0000002\n"
        "!v706!h\n"
        "!v880!S0044-59672019000300001\n"
        "!v012!Titulo em\n"
        "   varias   \n"
        "\n"
        "linhas^len\n"
        "!v083!^aResumo que cita !very e\n"
        "!ID do paciente\n"
        "!v10 sem fechamento^len\n"
        "!v040!pt\r\n"
        "!v030!Mem.\rInst.\n"
    )
    db_type = "artigo"

    def test_line_breaks_become_single_space(self):
        item = self.id_file.get("S0044-59672019000300001")
        self.assertEqual(2, len(item.records))
        h = item.records[1]
        self.assertEqual({"_": "Titulo em varias linhas", "l": "en"}, h["v012"][0])
        self.assertEqual(
            {"a": "Resumo que cita !very e !ID do paciente !v10 sem fechamento",
             "l": "en"},
            h["v083"][0],
        )
        self.assertEqual("pt", h["v040"][0]["_"])
        self.assertEqual("Mem. Inst.", h["v030"][0]["_"])

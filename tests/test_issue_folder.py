import os
import tempfile
from collections import Counter
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import PropertyMock, patch

from scielo_classic_website.models.issue_folder import (
    IssueFolder,
    _get_classic_website_rel_path,
)


def _write(path, content=b"x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


class TestIssueFolderFiles(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = os.path.join(self._tmp.name, "htdocs")
        bases = os.path.join(root, "bases")
        _write(os.path.join(bases, "xml", "abc", "v1n1", "a01.xml"), b"<article/>")
        _write(os.path.join(bases, "pdf", "abc", "v1n1", "a01.pdf"))
        _write(
            os.path.join(bases, "translation", "abc", "v1n1", "en_a01.htm"),
            b"<p>text</p>",
        )
        _write(os.path.join(root, "img", "revistas", "abc", "v1n1", "a01f1.jpg"))
        _write(os.path.join(root, "img", "fbpe", "abc", "v1n1", "a01f2.jpg"))
        # bases dentro da árvore de dois níveis acima de img/revistas:
        # a busca antiga (htdocs/**/acron/issue) alcançava bases/xml, bases/pdf...
        self.root = root
        self.paths = SimpleNamespace(
            bases_translation_path=os.path.join(bases, "translation"),
            bases_pdf_path=os.path.join(bases, "pdf"),
            bases_xml_path=os.path.join(bases, "xml"),
            htdocs_img_revistas_path=os.path.join(root, "img", "revistas"),
        )

    def tearDown(self):
        self._tmp.cleanup()

    def _files(self):
        return list(IssueFolder("abc", "v1n1", self.paths).files)

    def test_relative_path_is_unique(self):
        counter = Counter(item["relative_path"] for item in self._files())
        self.assertEqual([], [k for k, v in counter.items() if v > 1])

    def test_bases_files_are_not_assets(self):
        types = {item["name"]: item["type"] for item in self._files()}
        self.assertEqual("xml", types["a01.xml"])
        self.assertEqual("pdf", types["a01.pdf"])
        self.assertEqual("html", types["en_a01.htm"])

    def test_assets_from_img_revistas_and_fbpe(self):
        assets = sorted(
            item["name"] for item in self._files() if item["type"] == "asset"
        )
        self.assertEqual(["a01f1.jpg", "a01f2.jpg"], assets)

    def test_path_is_unique(self):
        counter = Counter(item["path"] for item in self._files())
        self.assertEqual([], [k for k, v in counter.items() if v > 1])

    def test_files_have_no_errors(self):
        self.assertEqual([], [item for item in self._files() if item.get("error")])

    def test_assets_relative_path(self):
        rel_paths = sorted(
            item["relative_path"] for item in self._files() if item["type"] == "asset"
        )
        self.assertEqual(
            [
                os.path.join("htdocs", "img", "fbpe", "abc", "v1n1", "a01f2.jpg"),
                os.path.join("htdocs", "img", "revistas", "abc", "v1n1", "a01f1.jpg"),
            ],
            rel_paths,
        )

    def test_assets_in_subfolders(self):
        _write(
            os.path.join(
                self.root, "img", "revistas", "abc", "v1n1", "suppl", "a01s1.pdf"
            )
        )
        assets = [
            item["name"] for item in self._files() if item["type"] == "asset"
        ]
        self.assertIn("a01s1.pdf", assets)

    def test_assets_of_other_issues_are_excluded(self):
        _write(os.path.join(self.root, "img", "revistas", "abc", "v1n2", "b01f1.jpg"))
        _write(os.path.join(self.root, "img", "revistas", "xyz", "v1n1", "c01f1.jpg"))
        _write(os.path.join(self.root, "img", "fbpe", "xyz", "v1n1", "d01f1.jpg"))
        names = [item["name"] for item in self._files()]
        self.assertNotIn("b01f1.jpg", names)
        self.assertNotIn("c01f1.jpg", names)
        self.assertNotIn("d01f1.jpg", names)

    def test_fbpe_nested_path(self):
        _write(
            os.path.join(
                self.root, "img", "fbpe", "old", "abc", "v1n1", "a01f3.jpg"
            )
        )
        assets = [
            item["name"] for item in self._files() if item["type"] == "asset"
        ]
        self.assertIn("a01f3.jpg", assets)

    def test_bases_under_fbpe_is_not_asset(self):
        # mesmo que bases esteja sob um caminho que case com o padrão fbpe,
        # seus arquivos não saem como asset
        bases = os.path.join(self.root, "fbpe", "bases")
        _write(os.path.join(bases, "xml", "abc", "v1n1", "a02.xml"), b"<article/>")
        self.paths.bases_xml_path = os.path.join(bases, "xml")
        items = [item for item in self._files() if item["name"] == "a02.xml"]
        self.assertEqual(["xml"], [item["type"] for item in items])
        assets = IssueFolder("abc", "v1n1", self.paths).htdocs_img_revistas_files
        self.assertNotIn("a02.xml", [item["name"] for item in assets])

    def test_translation_files(self):
        _write(
            os.path.join(
                self.root, "bases", "translation", "abc", "v1n1", "en_ba01.htm"
            ),
            b"<p>after</p>",
        )
        html = {
            item["name"]: item for item in self._files() if item["type"] == "html"
        }
        self.assertEqual(["en_a01.htm", "en_ba01.htm"], sorted(html))
        self.assertEqual("a01", html["en_a01.htm"]["key"])
        self.assertEqual("en", html["en_a01.htm"]["lang"])
        self.assertEqual("before", html["en_a01.htm"]["part"])
        self.assertEqual("a01", html["en_ba01.htm"]["key"])
        self.assertEqual("after", html["en_ba01.htm"]["part"])

    def test_pdf_translation_lang(self):
        _write(os.path.join(self.root, "bases", "pdf", "abc", "v1n1", "es_a01.pdf"))
        pdfs = {
            item["name"]: item for item in self._files() if item["type"] == "pdf"
        }
        self.assertIsNone(pdfs["a01.pdf"]["lang"])
        self.assertEqual("es", pdfs["es_a01.pdf"]["lang"])
        self.assertEqual("a01", pdfs["es_a01.pdf"]["key"])

    def test_missing_issue_folder(self):
        self.assertEqual([], list(IssueFolder("abc", "v9n9", self.paths).files))


class TestIssueFolderFilesDeduplication(TestCase):
    def _files(self, xml, translation, pdf, assets):
        with patch.object(
            IssueFolder, "bases_xml_files", new_callable=PropertyMock
        ) as m_xml, patch.object(
            IssueFolder, "bases_translation_files", new_callable=PropertyMock
        ) as m_translation, patch.object(
            IssueFolder, "bases_pdf_files", new_callable=PropertyMock
        ) as m_pdf, patch.object(
            IssueFolder, "htdocs_img_revistas_files", new_callable=PropertyMock
        ) as m_assets:
            m_xml.return_value = iter(xml)
            m_translation.return_value = iter(translation)
            m_pdf.return_value = iter(pdf)
            m_assets.return_value = iter(assets)
            return list(IssueFolder("abc", "v1n1", None).files)

    def test_keeps_first_occurrence(self):
        result = self._files(
            [{"type": "xml", "path": "/x/a01.xml"}],
            [{"type": "html", "path": "/x/en_a01.htm"}],
            [{"type": "pdf", "path": "/x/a01.pdf"}],
            [
                {"type": "asset", "path": "/x/a01.xml"},
                {"type": "asset", "path": "/x/en_a01.htm"},
                {"type": "asset", "path": "/x/a01.pdf"},
                {"type": "asset", "path": "/x/a01f1.jpg"},
            ],
        )
        self.assertEqual(
            [
                ("xml", "/x/a01.xml"),
                ("html", "/x/en_a01.htm"),
                ("pdf", "/x/a01.pdf"),
                ("asset", "/x/a01f1.jpg"),
            ],
            [(item["type"], item["path"]) for item in result],
        )

    def test_keeps_items_without_path(self):
        errors = [
            {"type": "html", "error": "e1", "error_type": "ValueError"},
            {"type": "asset", "error": "e2", "error_type": "ValueError"},
        ]
        result = self._files([], errors[:1], [], errors[1:])
        self.assertEqual(errors, result)


class TestGetClassicWebsiteRelPath(TestCase):
    def test_matches_whole_segment(self):
        self.assertEqual(
            os.path.join("bases", "xml", "abc", "v1n1", "a01.xml"),
            _get_classic_website_rel_path(
                os.path.join(
                    os.sep, "srv", "mybases", "bases", "xml", "abc", "v1n1", "a01.xml"
                )
            ),
        )

    def test_htdocs(self):
        self.assertEqual(
            os.path.join("htdocs", "img", "revistas", "abc", "v1n1", "a01f1.jpg"),
            _get_classic_website_rel_path(
                os.path.join(
                    os.sep, "srv", "myhtdocs", "htdocs", "img", "revistas",
                    "abc", "v1n1", "a01f1.jpg",
                )
            ),
        )

    def test_not_found(self):
        self.assertIsNone(
            _get_classic_website_rel_path(
                os.path.join(os.sep, "srv", "mybases", "img", "a01f1.jpg")
            )
        )

    def test_bases_work(self):
        self.assertEqual(
            os.path.join("bases-work", "abc", "abc.mst"),
            _get_classic_website_rel_path(
                os.path.join(os.sep, "data", "bases-work", "abc", "abc.mst")
            ),
        )


class TestIssueFolderIsBasesPath(TestCase):
    def setUp(self):
        self.folder = IssueFolder(
            "abc",
            "v1n1",
            SimpleNamespace(
                bases_xml_path="/data/bases/xml",
                bases_pdf_path="/data/bases/pdf",
                bases_translation_path=None,
                htdocs_img_revistas_path="/data/htdocs/img/revistas",
            ),
        )

    def test_inside_bases(self):
        self.assertTrue(self.folder._is_bases_path("/data/bases/xml/abc/v1n1/a01.xml"))
        self.assertTrue(self.folder._is_bases_path("/data/bases/pdf/abc/v1n1/a01.pdf"))

    def test_outside_bases(self):
        self.assertFalse(
            self.folder._is_bases_path("/data/htdocs/img/revistas/abc/v1n1/a.jpg")
        )

    def test_sibling_with_same_prefix(self):
        self.assertFalse(self.folder._is_bases_path("/data/bases/xml2/abc/a01.xml"))

    def test_relative_path(self):
        cwd = os.getcwd()
        folder = IssueFolder(
            "abc",
            "v1n1",
            SimpleNamespace(
                bases_xml_path="bases/xml",
                bases_pdf_path=None,
                bases_translation_path=None,
            ),
        )
        self.assertTrue(
            folder._is_bases_path(os.path.join(cwd, "bases", "xml", "abc", "a01.xml"))
        )

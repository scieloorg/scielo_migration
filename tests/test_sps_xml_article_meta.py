from unittest import TestCase

from lxml import etree

from scielo_migration.spsxml.sps_xml_article_meta import (
    XMLArticleMetaAffiliationPipe,
)
from scielo_migration.isisdb.journal_record import (
    JournalRecord,
)
from scielo_migration.isisdb.models import (
    Document,
    ArticleRecord,
    Journal,
)


def get_tree(xml_str):
    return etree.fromstring(xml_str)


def _get_journal():
    record = {
        "v068": [{"_": "jacron"}],
        "v100": [{"_": "Título do Periódico"}],
        "v150": [{"_": "Título Abreviado do Periódico"}],
        "v435": [{"_": "1234-5678", "t": "PRINT"}, {"_": "5678-1234", "t": "ONLIN"}, ],
        "v150": [{"_": "Título Abreviado do Periódico"}],
        "v310": [{"_": "BR"}],
        "v320": [{"_": "SP"}],
        "v490": [{"_": "São Paulo"}],
        "v480": [{"_": "XXX Society"}],
    }
    journal_record = JournalRecord(record)
    return Journal(journal_record)


def _get_document(data):
    h_record = ArticleRecord(data)
    journal = _get_journal()
    return Document(h_record, journal)


class TestXMLArticleMetaAffiliationPipe(TestCase):

    def setUp(self):
        document_data = {
            "v070": [
                {
                    "p": "Brasil",
                    "c": "São Paulo",
                    "_": "Fundação Getulio Vargas",
                    "1": "Escola de Administração de Empresas de São Paulo",
                    "i": "aff1",
                    "l": "1",
                    "s": "SP",
                    "e": "autor@foo.com"
                }
            ],
        }
        document = _get_document(document_data)
        print(document.affiliations)
        xml = (
            '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) '
            'Journal Publishing DTD v1.0 20120330//EN" '
            '"JATS-journalpublishing1.dtd">\n'
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        self.data = document, etree.fromstring(xml)

    def test_transform(self):
        transformed = XMLArticleMetaAffiliationPipe().transform(self.data)
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '<aff id="aff1">'
            '<institution content-type="orgname">Fundação Getulio Vargas</institution>'
            '<institution content-type="orgdiv1">Escola de Administração de Empresas de São Paulo</institution>'
            '<addr-line>'
            '<named-content content-type="city">São Paulo</named-content>'
            '<named-content content-type="state">SP</named-content>'
            '</addr-line>'
            '<country country="BR">Brasil</country>'
            '<email>autor@foo.com</email>'
            '</aff>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        result = etree.tostring(transformed[1], encoding="utf-8").decode("utf-8")
        print()
        print(expected)
        print(result)
        self.assertEqual(expected, result)

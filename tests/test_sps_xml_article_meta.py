from unittest import TestCase

from lxml import etree

from scielo_migration.spsxml.sps_xml_article_meta import (
    XMLArticleMetaAffiliationPipe,
    XMLArticleMetaPublicationDatesPipe,
    XMLArticleMetaIssueInfoPipe,
    XMLArticleMetaElocationInfoPipe,
    XMLArticleMetaPagesInfoPipe,
)
from scielo_migration.isisdb.xylose import Article


def tostring(node):
    return etree.tostring(node, encoding="utf-8").decode("utf-8")


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
    return {"title": record}


def _get_document(data):
    data = {"article": data}
    data.update(_get_journal())
    return Article(data)


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
        result = tostring(transformed[1])
        self.assertEqual(expected, result)


class TestXMLArticleMetaPublicationDatesPipe(TestCase):

    def setUp(self):
        # https://articlemeta.scielo.org/api/v1/article/?collection=scl&code=S0103-20032019000300379
        document_data = {
            "v065": [
                {
                    "_": "20190000"
                }
            ],
            "v223": [
                {
                    "_": "20190916"
                }
            ],
        }
        document = _get_document(document_data)
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
        transformed = XMLArticleMetaPublicationDatesPipe().transform(self.data)
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '<pub-date publication-format="electronic" date-type="pub">'
            '<day>16</day>'
            '<month>09</month>'
            '<year>2019</year>'
            '</pub-date>'
            '<pub-date publication-format="electronic" date-type="collection">'
            '<year>2019</year>'
            '</pub-date>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        result = tostring(transformed[1])
        self.assertEqual(expected, result)


class TestXMLArticleMetaIssueInfoPipe(TestCase):

    def _get_document(self, document_data=None):
        document_data_default = {
            "v031": [
                {
                    "_": "4"
                }
            ],
            "v032": [
                {
                    "_": "1"
                }
            ],
            "v132": [
                {
                    "_": "B"
                }
            ],
        }
        document = _get_document(document_data or document_data_default)
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
        return document, etree.fromstring(xml)

    def test_transform_v4n1sB(self):
        transformed = XMLArticleMetaIssueInfoPipe().transform(
            self._get_document())
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '<volume>4</volume>'
            '<issue>1</issue>'
            '<supplement>B</supplement>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        result = tostring(transformed[1])
        self.assertEqual(expected, result)

    def test_transform_v4(self):
        d = {
            "v031": [
                {
                    "_": "4"
                }
            ]
        }
        transformed = XMLArticleMetaIssueInfoPipe().transform(
            self._get_document(d))
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '<volume>4</volume>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        result = tostring(transformed[1])
        self.assertEqual(expected, result)

    def test_transform_n2(self):
        d = {
            "v032": [
                {
                    "_": "2"
                }
            ]
        }
        transformed = XMLArticleMetaIssueInfoPipe().transform(
            self._get_document(d))
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '<issue>2</issue>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        result = tostring(transformed[1])
        self.assertEqual(expected, result)

    def test_transform_n2s0(self):
        d = {
            "v032": [
                {
                    "_": "2"
                }
            ],
            "v132": [
                {
                    "_": "0"
                }
            ]
        }
        transformed = XMLArticleMetaIssueInfoPipe().transform(
            self._get_document(d))
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '<issue>2</issue>'
            '<supplement>0</supplement>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        result = tostring(transformed[1])
        self.assertEqual(expected, result)

    def test_transform_v2s1(self):
        d = {
            "v031": [
                {
                    "_": "2"
                }
            ],
            "v132": [
                {
                    "_": "1"
                }
            ]
        }
        transformed = XMLArticleMetaIssueInfoPipe().transform(
            self._get_document(d))
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta>'
            '<volume>2</volume>'
            '<supplement>1</supplement>'
            '</article-meta>'
            '</front>'
            '</article>'
        )
        result = tostring(transformed[1])
        self.assertEqual(expected, result)

    def test_transform_aop(self):
        d = {
            "v032": [
                {
                    "_": "ahead"
                }
            ],
        }
        transformed = XMLArticleMetaIssueInfoPipe().transform(
            self._get_document(d))
        expected = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<article-meta/>'
            '</front>'
            '</article>'
        )
        result = tostring(transformed[1])
        self.assertEqual(expected, result)



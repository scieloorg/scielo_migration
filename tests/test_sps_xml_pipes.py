from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.sps_xml_pipes import (
    get_xml_rsps,
    SetupArticlePipe,
    XMLClosePipe,
)
from scielo_classic_website.isisdb.journal_record import (
    JournalRecord,
)
from scielo_classic_website.models.document import (
    Document,
    ArticleRecord,
)
from scielo_classic_website.models.journal import (
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


def _get_article_record_content():
    return {
        "v002": [{"_": "S0044-5967(99)000300260"}],
        "v880": [{"_": "S0044-59671999000300260"}],
        "v881": [{"_": "S0044-59671998005000260"}],
        "v885": [{"_": "zGfhXPfmQxVkLNzXy9FTkFf"}],
        "v121": [{"_": "00260"}],
        "v237": [{"_": "10.1590/adjdadla"}],
        "v049": [{"_": "Biotechnology"}],
    }


class TestGetXmlRsps(TestCase):

    def test_get_xml_rsps(self):
        h_record = ArticleRecord(_get_article_record_content())
        journal = _get_journal()
        document = Document(h_record, journal)
        expected = (
            '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) '
            'Journal Publishing DTD v1.0 20120330//EN" '
            '"JATS-journalpublishing1.dtd">\n'
            '<article xmlns:xlink="http://www.w3.org/1999/xlink" '
            'specific-use="sps-1.4" dtd-version="1.0">'
            '<front>'
            '<journal-meta>'
            '<journal-id journal-id-type="publisher-id">jacron</journal-id>'
            '<journal-title-group>'
            '<journal-title>Título do Periódico</journal-title>'
            '<abbrev-journal-title abbrev-type="publisher">Título Abreviado do Periódico</abbrev-journal-title>'
            '</journal-title-group>'
            '<issn pub-type="ppub">1234-5678</issn>'
            '<issn pub-type="epub">5678-1234</issn>'
            '<publisher>'
            '<publisher-name>XXX Society</publisher-name>'
            '<publisher-loc>São Paulo, SP, Brazil</publisher-loc>'
            '</publisher>'
            '</journal-meta>'
            '<article-meta>'
            '<article-id pub-id-type="publisher-id" specific-use="scielo-v1">S0044-5967(99)000300260</article-id>'
            '<article-id pub-id-type="publisher-id" specific-use="scielo-v2">S0044-59671999000300260</article-id>'
            '<article-id pub-id-type="publisher-id" specific-use="scielo-v3">zGfhXPfmQxVkLNzXy9FTkFf</article-id>'
            '<article-id specific-use="previous-pid">S0044-59671998005000260</article-id>'
            '<article-id pub-id-type="other">00260</article-id>'
            '<article-id pub-id-type="doi">10.1590/adjdadla</article-id>'
            '<article-categories>'
                '<subj-group subj-group-type="heading">'
                    '<subject>Biotechnology</subject>'
                '</subj-group>'
            '</article-categories>'
            '</article-meta>'
            '</front>'
            '</article>'
        ).encode("utf-8")
        result = get_xml_rsps(document)
        print(result)
        self.assertEqual(expected, result)


class TestSetupArticlePipe(TestCase):

    def test_SetupArticlePipe(self):
        data = None, None
        _raw, _xml = SetupArticlePipe().transform(data)
        self.assertEqual('sps-1.4', _xml.get("specific-use"))
        self.assertEqual('1.0', _xml.get("dtd-version"))


class TestXMLClosePipe(TestCase):
    def test_XMLClosePipe(self):
        data = None, etree.fromstring("<article/>")
        _xml = XMLClosePipe().transform(data)
        expected = (
            '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) '
            'Journal Publishing DTD v1.0 20120330//EN" '
            '"JATS-journalpublishing1.dtd">\n'
            '<article/>'
        ).encode("utf-8")
        self.assertEqual(expected, _xml)

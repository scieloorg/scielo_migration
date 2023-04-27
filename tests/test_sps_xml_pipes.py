from unittest import TestCase

from lxml import etree

from scielo_classic_website.models.document import Document
from scielo_classic_website.spsxml.sps_xml_pipes import (
    SetupArticlePipe,
    XMLClosePipe,
    get_xml_rsps
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
    return {"title": record}


def _get_article_record_content():
    data = {
        "v002": [{"_": "S0044-5967(99)000300260"}],
        "v880": [{"_": "S0044-59671999000300260"}],
        "v881": [{"_": "S0044-59671998005000260"}],
        "v885": [{"_": "zGfhXPfmQxVkLNzXy9FTkFf"}],
        "v121": [{"_": "00260"}],
        "v237": [{"_": "10.1590/adjdadla"}],
        "v049": [{"_": "Biotechnology"}],
        "v040": [{"_": "es"}],
        "v012": [
            {"_": "Conocimientos de los pediatras sobre la laringomalacia: ¿siempre es un proceso banal?", "l": "es"},
            {"_": "Pediatrician knowledge about laryngomalacia: is it always a banal process?", "l": "en"},
        ],
        "v010": [
            {"n": "Albert", "s": "Einstein", "r": "ND", "k": "0000-0001-8528-2091"},
            {"n": "Rogerio", "s": "Meneghini", "r": "ND", "l": "4760273612238540"},
        ],
    }
    return {"article": data}


class TestGetXmlRsps(TestCase):

    def test_get_xml_rsps(self):
        data = _get_article_record_content()
        data.update(_get_journal())
        document = Document(data)
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
            '<title-group>'
            '<article-title>Conocimientos de los pediatras sobre la laringomalacia: ¿siempre es un proceso banal?</article-title>'
            '<trans-title-group xml:lang="en">'
                    '<trans-title>Pediatrician knowledge about laryngomalacia: is it always a banal process?</trans-title>'
            '</trans-title-group>'
            '</title-group>'
            '<contrib-group>'
                '<contrib contrib-type="author">'
                    '<contrib-id contrib-id-type="orcid">0000-0001-8528-2091</contrib-id>'
                    '<name>'
                        '<surname>Einstein</surname>'
                        '<given-names>Albert</given-names>'
                    '</name>'
                '</contrib>'
                '<contrib contrib-type="author">'
                    '<contrib-id contrib-id-type="lattes">4760273612238540</contrib-id>'
                    '<name>'
                        '<surname>Meneghini</surname>'
                        '<given-names>Rogerio</given-names>'
                    '</name>'
                '</contrib>'
            '</contrib-group>'
            '</article-meta>'
            '</front>'
            '</article>'
        ).encode("utf-8")
        result = get_xml_rsps(document)
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

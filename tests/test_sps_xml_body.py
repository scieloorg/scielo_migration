from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.sps_xml_body_pipes import OlPipe, TagsHPipe, UlPipe


def get_tree(xml_str):
    return etree.fromstring(xml_str)


class TestOlPipe(TestCase):
    def test_ol_pipe(self):
        raw = None
        xml = get_tree("<root><body><ol>Um</ol></body></root>")
        expected = (
            "<root>"
            "<body>"
            '<list list-type="order">'
            "Um"
            "</list>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)
        _raw, _xml = OlPipe().transform(data)
        result = etree.tostring(_xml, encoding="utf-8").decode("utf-8")
        self.assertEqual(1, len(_xml.xpath(".//list[@list-type='order']")))
        self.assertEqual(expected, result)


class TestUlPipe(TestCase):
    def test_ul_pipe(self):
        raw = None
        xml = get_tree("<root><body><ul>Um</ul></body></root>")
        expected = (
            "<root>"
            "<body>"
            '<list list-type="bullet">'
            "Um"
            "</list>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, _xml = UlPipe().transform(data)
        result = etree.tostring(_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(1, len(_xml.xpath(".//list[@list-type='bullet']")))
        self.assertEqual(expected, result)


class TestTagsHPipe(TestCase):
    def test_transform_substitui_tags_de_cabecalho_por_tags_title(self):
        xml = get_tree(
            "<root><body><h1>Título 1</h1><h2>Título 2</h2><h3>Título 3</h3></body></root>"
        )
        content = (
            "<root>"
            "<body>"
            '<title content-type="h1">Título 1</title>'
            '<title content-type="h2">Título 2</title>'
            '<title content-type="h3">Título 3</title>'
            "</body>"
            "</root>"
        )

        # Cria objeto etree a partir de content.
        expected_element = etree.fromstring(content)
        data = (None, xml)

        _, transformed_xml = TagsHPipe().transform(data)

        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)

from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.sps_xml_body_pipes import (
    OlPipe,
    TagsHPipe,
    UlPipe,
    ASourcePipe,
    ANamePipe,
)


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


class TestASourcePipe(TestCase):
    def test_transform_muda_src_para_href_em_nos_a(self):
        xml = get_tree('<root><body><a src="foo.jpg">Imagem</a></body></root>')
        expected = '<root><body><a href="foo.jpg">Imagem</a></body></root>'
        data = (None, xml)

        _, transformed_xml = ASourcePipe().transform(data)

        expected_element = etree.fromstring(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)

    def test_transform_nao_altera_nos_a_sem_src(self):
        xml = get_tree('<root><body><a href="foo.jpg">Imagem</a></body></root>')
        data = (None, xml)

        _, transformed_xml = ASourcePipe().transform(data)

        expected = '<root><body><a href="foo.jpg">Imagem</a></body></root>'
        expected_element = etree.fromstring(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode(
            "utf-8"
        )
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)


class TestAHrefPipe(TestCase):
    ...


class TestANamePipe(TestCase):
    def test_transform_substitui_nos_a_por_divs_com_id(self):
        xml = get_tree('<root><body><a name="secao1">Seção 1</a></body></root>')
        expected = '<root><body><div id="secao1">Seção 1</div></body></root>'
        data = (None, xml)

        _, transformed_xml = ANamePipe().transform(data)

        expected_element = etree.fromstring(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)

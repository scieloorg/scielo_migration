from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.sps_xml_body_pipes import (
    ANamePipe,
    ASourcePipe,
    ImgSrcPipe,
    OlPipe,
    RemoveCDATAPipe,
    FontSymbolPipe,
    TagsHPipe,
    UlPipe,
)


def get_tree(xml_str):
    return etree.fromstring(xml_str)


class TestRemoveCDATAPipe(TestCase):
    def test_transform_remove_CDATA(self):
        xml = get_tree('<root><![CDATA[Exemplo CDATA.]]></root>')
        expected = '<root>Exemplo CDATA.</root>'
        data = (None, xml)

        _, transformed_xml = RemoveCDATAPipe().transform(data)

        expected_element = get_tree(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)


class TestFontSymbolPipe(TestCase):
    def test_transform_font_symbol_pipe(self):
        xml = get_tree('<root><font face="symbol">simbolo</font></root>')
        expected = '<root><font-face-symbol face="symbol">simbolo</font-face-symbol></root>'
        data = (None, xml)

        _, transformed_xml = FontSymbolPipe().transform(data)

        expected_element = get_tree(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)


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
        expected_element = get_tree(content)
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

        expected_element = get_tree(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)

    def test_transform_nao_altera_nos_a_sem_src(self):
        xml = get_tree('<root><body><a href="foo.jpg">Imagem</a></body></root>')
        data = (None, xml)

        _, transformed_xml = ASourcePipe().transform(data)

        expected = '<root><body><a href="foo.jpg">Imagem</a></body></root>'
        expected_element = get_tree(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
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

        expected_element = get_tree(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)


class TestImgSrcPipe(TestCase):
    def test_transform_substitui_tags_img_por_grafico_com_href(self):
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<img src="foo.jpg"></img>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<graphic xlink:href="foo.jpg"/>'
            "</body>"
            "</root>"
        )
        data = (None, xml)

        _, transformed_xml = ImgSrcPipe().transform(data)

        expected_element = get_tree(expected)
        expected = etree.tostring(expected_element, encoding="utf-8").decode("utf-8")
        result = etree.tostring(transformed_xml, encoding="utf-8").decode("utf-8")

        self.assertEqual(expected, result)

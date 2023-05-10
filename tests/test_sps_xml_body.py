from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.sps_xml_body_pipes import (
    AHrefPipe,
    ANamePipe,
    ASourcePipe,
    EndPipe,
    FontSymbolPipe,
    ImgSrcPipe,
    MainHTMLPipe,
    OlPipe,
    RemoveCDATAPipe,
    RemoveCommentPipe,
    RemoveTagsPipe,
    RenameElementsPipe,
    StylePipe,
    TagsHPipe,
    TranslatedHTMLPipe,
    UlPipe,
    XRefTypePipe,
)


def get_tree(xml_str):
    return etree.fromstring(xml_str)


def tree_tostring_decode(_str):
    return etree.tostring(_str, encoding="utf-8").decode("utf-8")


class TestAHrefPipe(TestCase):
    def test_transform(self):
        xml = get_tree(
            (
                "<root>"
                '<a href="http://scielo.org">Example</a>'
                '<a href="mailto:james@scielo.org">James</a>'
                '<a href="#section1">Seção 1</a>'
                '<a href="/img/revistas/logo.jpg">Logo</a>'
                "</root>"
            )
        )
        expected = (
            "<root>"
            '<ext-link xmlns:ns0="http://www.w3.org/1999/xlink" ext-link-type="uri" ns0:href="http://scielo.org">'
            "Example"
            "</ext-link>"
            "<email/>"
            '<xref rid="section1">Seção 1</xref>'
            '<xref rid="img/revistas/logo.jpg">Logo</xref>'
            "</root>"
        )

        data = (None, xml)

        _, transformed_xml = AHrefPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class MockMainDocument:
    def __init__(self):
        self.main_html_paragraphs = {
            "before references": [
                {
                    "text": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                    "index": "1",
                    "reference_index": "",
                    "part": "before references",
                },
                {
                    "text": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                    "index": "2",
                    "reference_index": "",
                    "part": "before references",
                },
            ],
            "references": [
                {
                    "text": (
                        "<!-- ref --><P><B>Abu-Lughod, Janet Lippman</B> (1995):"
                        ' "Comparing Chicago, New York y Los Angeles:'
                        ' testing some world cities hypotheses". In Paul L. Knox y Peter J. Taylor (eds.)'
                        " World Cities in a Worldsystem."
                        " Cambridge, UK: Cambridge University Press, pp.171-191.    <BR>&nbsp;"
                    ),
                    "index": "1",
                    "reference_index": "1",
                    "part": "references",
                },
                {
                    "text": "<!-- ref --><P><B>Abu-Lughod, Janet Lippman</B> (1995)</P>",
                    "index": "2",
                    "reference_index": "2",
                    "part": "references",
                },
            ],
            "after references": [
                {
                    "text": "<p>Depois das referencias 1</p>",
                    "index": "",
                    "reference_index": "",
                    "part": "after references",
                },
                {
                    "text": "<p>Depois das referencias 2</p>",
                    "index": "",
                    "reference_index": "",
                    "part": "after references",
                },
            ],
        }


class TestMainHTMLPipe(TestCase):
    def test_transform(self):
        raw = MockMainDocument()
        expected = (
            "<article>"
            "<body>"
            "<p>"
            "<![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</p>"
            "<p>"
            "<![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</p>"
            "</body>"
            "<back>"
            "<ref-list>"
            '<ref id="B1">'
            "<mixed-citation>"
            "<![CDATA[<!-- ref -->"
            "<P>"
            "<B>Abu-Lughod, Janet Lippman</B> (1995):"
            ' "Comparing Chicago, New York y Los Angeles:'
            ' testing some world cities hypotheses". In Paul L. Knox y Peter J. Taylor (eds.)'
            " World Cities in a Worldsystem."
            " Cambridge, UK: Cambridge University Press, pp.171-191.    <BR>&nbsp;]]>"
            "</mixed-citation>"
            "</ref>"
            '<ref id="B2">'
            "<mixed-citation>"
            "<![CDATA[<!-- ref -->"
            "<P>"
            "<B>Abu-Lughod, Janet Lippman</B> (1995)</P>]]>"
            "</mixed-citation>"
            "</ref>"
            "</ref-list>"
            "<sec>"
            "<![CDATA[<p>Depois das referencias 1</p>]]>"
            "</sec>"
            "<sec>"
            "<![CDATA[<p>Depois das referencias 2</p>]]>"
            "</sec>"
            "</back>"
            "</article>"
        )
        xml = get_tree("<article><body></body><back></back></article>")
        data = (raw, xml)

        _, transformed_xml = MainHTMLPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class MockTranslatedDocument:
    def __init__(self):
        self.translated_html_by_lang = {
            "pt": {
                "before references": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                "after references": "<p>Depois das referencias 1</p>",
            },
            "en": {
                "before references": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                "after references": "<p>After Reference</p>",
            },
        }


class TestTranslatedHTMLPipe(TestCase):
    def test_transform(self):
        raw = MockTranslatedDocument()
        expected = (
            "<article>"
            "<body/>"
            "<back>"
            '<sub-article article-type="translation" xml:lang="pt">'
            "<body><![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</body>"
            "<back>"
            "<![CDATA[<p>Depois das referencias 1</p>]]>"
            '<sub-article article-type="translation" xml:lang="en">'
            "<body>"
            "<![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</body>"
            "<back>"
            "<![CDATA[<p>After Reference</p>]]>"
            "</back>"
            "</sub-article>"
            "</back>"
            "</sub-article>"
            "</back>"
            "</article>"
        )
        xml = get_tree("<article><body></body><back></back></article>")
        data = (raw, xml)

        _, transformed_xml = TranslatedHTMLPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestEndPipe(TestCase):
    def test_transform_remove_CDATA(self):
        xml = get_tree("<root><body>Texto</body></root>")
        expected = b"<root><body>Texto</body></root>"
        data = (None, xml)

        result = EndPipe().transform(data)
        self.assertEqual(expected, result)


class TestRemoveCDATAPipe(TestCase):
    def test_transform_remove_CDATA(self):
        xml = get_tree("<root><![CDATA[Exemplo CDATA.]]></root>")
        expected = "<root>Exemplo CDATA.</root>"
        data = (None, xml)

        _, transformed_xml = RemoveCDATAPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestRemoveCommentPipe(TestCase):
    def test_transform_remove_comment(self):
        xml = get_tree("<root><body><!-- comentario --><p>Um</p></body></root>")
        expected = "<root><body><p>Um</p></body></root>"
        data = (None, xml)

        _, transformed_xml = RemoveCommentPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestRemoveTagsPipe(TestCase):
    def setUp(self):
        self.xml = get_tree(
            (
                "<root>"
                "<body>"
                "<p><span>Texto</span></p>"
                "<center>Texto centralizado</center>"
                "<s>Sublinhado</s>"
                "<lixo>Lixo</lixo>"
                "</body>"
                "</root>"
            )
        )

    def test_transform_remove_tags(self):
        expected = (
            "<root><body><p>Texto</p>Texto centralizadoSublinhadoLixo</body></root>"
        )
        data = (None, self.xml)

        _, transformed_xml = RemoveTagsPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestRenameElementsPipe(TestCase):
    def test_transform_rename_elements(self):
        xml = get_tree(
            (
                "<root>"
                "<div>Um</div>"
                "<dir>"
                "<li>Item 1</li>"
                "<li>Item 2</li>"
                "</dir>"
                "<dl>"
                "<dt>Termo 1</dt>"
                "<dd>Definição 1</dd>"
                "<dt>Termo 2</dt>"
                "<dd>Definição 2</dd>"
                "</dl>"
                "<br></br>"
                "<blockquote>Quote</blockquote>"
                "</root>"
            )
        )
        expected = (
            "<root>"
            "<sec>Um</sec>"
            "<ul>"
            "<list-item>Item 1</list-item>"
            "<list-item>Item 2</list-item>"
            "</ul>"
            "<def-list>"
            "<dt>Termo 1</dt>"
            "<def-item>Definição 1</def-item>"
            "<dt>Termo 2</dt>"
            "<def-item>Definição 2</def-item>"
            "</def-list>"
            "<break/>"
            "<disp-quote>Quote</disp-quote>"
            "</root>"
        )
        data = (None, xml)

        _, transformed_xml = RenameElementsPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

    def test_transform_rename_elements_empty_xml(self):
        expected = "<root/>"
        data = (None, etree.fromstring("<root/>"))

        _, transformed_xml = RenameElementsPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestFontSymbolPipe(TestCase):
    def test_transform_font_symbol_pipe(self):
        xml = get_tree('<root><font face="symbol">simbolo</font></root>')
        expected = (
            '<root><font-face-symbol face="symbol">simbolo</font-face-symbol></root>'
        )
        data = (None, xml)

        _, transformed_xml = FontSymbolPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestStylePipe(TestCase):
    def test_transform_style(self):
        xml = get_tree(
            (
                "<root>"
                "<body>"
                "<p><span name='style_bold'>bold text</span></p>"
                "<p><span name='style_italic'>italic text</span></p>"
                "<p><span name='style_sup'>sup text</span></p>"
                "<p><span name='style_sub'>sub text</span></p>"
                "<p><span name='style_underline'>underline text</span></p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            "<root>"
            "<body>"
            '<p><bold name="style_bold">bold text</bold></p>'
            '<p><italic name="style_italic">italic text</italic></p>'
            '<p><sup name="style_sup">sup text</sup></p>'
            '<p><sub name="style_sub">sub text</sub></p>'
            '<p><underline name="style_underline">underline text</underline></p>'
            "</body>"
            "</root>"
        )
        data = (None, xml)

        _, transformed_xml = StylePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
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
        result = tree_tostring_decode(_xml)

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
        result = tree_tostring_decode(_xml)

        self.assertEqual(1, len(_xml.xpath(".//list[@list-type='bullet']")))
        self.assertEqual(expected, result)


class TestTagsHPipe(TestCase):
    def test_transform_substitui_tags_de_cabecalho_por_tags_title(self):
        xml = get_tree(
            "<root><body><h1>Título 1</h1><h2>Título 2</h2><h3>Título 3</h3></body></root>"
        )
        expected = (
            "<root>"
            "<body>"
            '<title content-type="h1">Título 1</title>'
            '<title content-type="h2">Título 2</title>'
            '<title content-type="h3">Título 3</title>'
            "</body>"
            "</root>"
        )

        data = (None, xml)

        _, transformed_xml = TagsHPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestASourcePipe(TestCase):
    def test_transform_muda_src_para_href_em_nos_a(self):
        xml = get_tree('<root><body><a src="foo.jpg">Imagem</a></body></root>')
        expected = '<root><body><a href="foo.jpg">Imagem</a></body></root>'
        data = (None, xml)

        _, transformed_xml = ASourcePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

    def test_transform_nao_altera_nos_a_sem_src(self):
        xml = get_tree('<root><body><a href="foo.jpg">Imagem</a></body></root>')
        data = (None, xml)

        _, transformed_xml = ASourcePipe().transform(data)

        expected = '<root><body><a href="foo.jpg">Imagem</a></body></root>'
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestANamePipe(TestCase):
    def test_transform_substitui_nos_a_por_divs_com_id(self):
        xml = get_tree('<root><body><a name="secao1">Seção 1</a></body></root>')
        expected = '<root><body><div id="secao1">Seção 1</div></body></root>'
        data = (None, xml)

        _, transformed_xml = ANamePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
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
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestXRefTypePipe(TestCase):
    def test_ol_pipe(self):
        raw = None
        xml = get_tree('<root><body><xref rid="t1">Table 1</xref></body></root>')
        expected = (
            '<root><body><xref rid="t1" ref-type="table">Table 1</xref></body></root>'
        )
        data = (raw, xml)

        _, transformed_xml = XRefTypePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

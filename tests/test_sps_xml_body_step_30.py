"""
Testes para a etapa `convert_html_to_xml_step_30_embed_html` do pipeline
de conversão de HTML para XML (terceira chamada da sequência em
`convert_html_to_xml`).

Cobre os comportamentos de robustez introduzidos para evitar que a etapa
falhe com `XMLSyntaxError` (originando o erro reportado no Article Proc do
serviço migrador) e para preservar o estado do documento quando a mesclagem
de HTML embutido falhar parcialmente.
"""
from unittest import TestCase
from unittest import mock

from lxml import etree as ET

from scielo_classic_website.spsxml import sps_xml_body_pipes
from scielo_classic_website.spsxml.sps_xml_body_pipes import (
    MarkHTMLFileToEmbedPipe,
    StartPipe,
)


class _Journal:
    def __init__(self, acronym="abc"):
        self.acronym = acronym


class _Raw:
    def __init__(self, xml_body_and_back=None, journal=None, html_reader=None):
        self.xml_body_and_back = xml_body_and_back or []
        self.journal = journal
        if html_reader is not None:
            self.html_reader = html_reader


class TestStartPipeRecover(TestCase):
    def test_parses_valid_xml(self):
        raw = _Raw(xml_body_and_back=["<article><body><p>ok</p></body></article>"])
        _, xml = StartPipe().transform(raw)
        self.assertEqual(xml.tag, "article")
        self.assertEqual(xml.find(".//p").text, "ok")

    def test_recovers_from_invalid_comment_with_double_hyphen(self):
        # Comentário inválido para XML (contém '--' interno) — clipboard do MS
        # pode introduzir esse padrão. Antes da correção, isso quebrava o
        # passo 30 com XMLSyntaxError.
        raw = _Raw(
            xml_body_and_back=[
                "<article><body><p>ok</p>"
                "<!--EndF>><!--EndFragment--></body></article>"
            ]
        )
        _, xml = StartPipe().transform(raw)
        self.assertEqual(xml.tag, "article")
        self.assertEqual(xml.find(".//p").text, "ok")


class TestMarkHTMLFileToEmbedPipeMerge(TestCase):
    def _build_xml(self):
        return ET.fromstring(
            "<article>"
            "<body><p>body content</p></body>"
            "<back><ref>r1</ref></back>"
            "</article>"
        )

    def test_back_tag_preserved_when_merge_html_returns_none(self):
        """Se merge_html falhar e retornar None, a tag <back> deve ser
        restaurada — antes da correção, ela permanecia como <body>."""
        raw = _Raw(journal=_Journal())
        xml = self._build_xml()
        with mock.patch.object(sps_xml_body_pipes, "merge_html", return_value=None):
            MarkHTMLFileToEmbedPipe().transform((raw, xml))
        self.assertIsNotNone(xml.find(".//back"))
        self.assertIsNotNone(xml.find(".//body"))

    def test_back_tag_preserved_when_merge_html_raises(self):
        """Se merge_html lançar exceção ao processar <back>, a tag original
        deve ser restaurada e a transformação deve concluir sem propagar."""
        raw = _Raw(journal=_Journal())
        xml = self._build_xml()
        with mock.patch.object(
            sps_xml_body_pipes, "merge_html", side_effect=RuntimeError("boom")
        ):
            # Não deve levantar exceção
            MarkHTMLFileToEmbedPipe().transform((raw, xml))
        self.assertIsNotNone(xml.find(".//back"))
        self.assertIsNotNone(xml.find(".//body"))

    def test_back_failure_does_not_block_body_processing(self):
        """Falha em <back> não deve impedir a substituição bem-sucedida em
        <body>, e vice-versa."""
        raw = _Raw(journal=_Journal())
        xml = self._build_xml()

        new_body = ET.fromstring("<body><p>merged body</p></body>")

        def fake_merge_html(input_html, **kwargs):
            if "<back" in input_html or "back content" in input_html:
                raise RuntimeError("back failure")
            # Para <body>, retorna um elemento válido
            return ET.fromstring("<body><p>merged body</p></body>")

        with mock.patch.object(
            sps_xml_body_pipes, "merge_html", side_effect=fake_merge_html
        ):
            MarkHTMLFileToEmbedPipe().transform((raw, xml))

        # body foi substituído com sucesso
        self.assertEqual(xml.find(".//body/p").text, "merged body")
        # back foi preservado
        self.assertIsNotNone(xml.find(".//back"))


class TestHTMLMergerInternalReturnsNoneOnError(TestCase):
    def test_process_html_internal_returns_none_on_parse_failure(self):
        from scielo_classic_website.htmlbody.html_merger import HTMLMerger

        merger = HTMLMerger()
        # Faz a função interna do parser explodir
        with mock.patch(
            "scielo_classic_website.htmlbody.html_merger.html.fromstring",
            side_effect=RuntimeError("boom"),
        ):
            result = merger.process_html_internal("<html><body/></html>")
        self.assertIsNone(result)

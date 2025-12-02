import traceback
import sys
import logging
import os
from copy import deepcopy
import re

import plumber
from lxml import etree as ET

from scielo_classic_website.htmlbody.html_fixer import remove_tags
from scielo_classic_website.htmlbody.html_body import HTMLContent
from scielo_classic_website.spsxml.sps_xml_article_meta import XMLNormalizeSpacePipe
from scielo_classic_website.utils.body_sec_type_matcher import get_sectype
from scielo_classic_website.htmlbody.name2number import fix_pre_loading
from scielo_migration.scielo_classic_website.spsxml.detector import (
    analyze_xref,
    detect_from_text,
)
from scielo_migration.scielo_classic_website.htmlbody.html_embedder import (
    get_html_to_embed,
)
from scielo_migration.scielo_classic_website.spsxml.detector_config_xref import (
    ASSET_TYPE_CONFIG,
)


class XMLBodyAnBackConvertException(Exception): ...


def delete_tags(root):
    for node in root.xpath(f"//*[@delete]"):
        parent = node.getparent()
        node.addnext(ET.Element("EMPTYTAGTOSTRIP"))
        parent.remove(node)

    ET.strip_tags(root, "EMPTYTAGTOSTRIP")


def _report(xml, func_name):
    # logging.info(f"Function: {func_name}")
    # logging.info(
    #     ET.tostring(
    #         xml,
    #         encoding="utf-8",
    #         method="xml",
    #     ).decode(
    #         "utf-8"
    #     )[:500]
    # )
    pass


def text_to_node(element_name, children_data_as_text):
    if not element_name:
        raise ValueError("element_name cannot be empty")
    if not children_data_as_text:
        return ET.Element(element_name)

    # padroniza entidades
    fixed_html_entities = fix_pre_loading(children_data_as_text)
    try:
        return ET.fromstring(f"<{element_name}>{fixed_html_entities}</{element_name}>")
    except Exception as e:
        pass
    try:
        return get_node_from_standardized_html(element_name, fixed_html_entities)
    except Exception as e:
        return ET.fromstring(
            f"<{element_name}>{remove_tags(fixed_html_entities)}</{element_name}>"
        )


def get_node_from_standardized_html(element_name, fixed_html_entities):
    if element_name != "body":
        fixed_html_entities = f"<{element_name}>{fixed_html_entities}</{element_name}>"
    try:
        hc = HTMLContent(fixed_html_entities)
        node = hc.tree.find(f".//{element_name}")
        if node is None:
            raise ValueError("Unable to get node from html")
        if node.xpath(".//*") or "".join(node.itertext()):
            raise ValueError("Unable to get node from html")
        return node
    except Exception as e:
        raise ValueError("Unable to get node from html")


def convert_html_to_xml(document):
    """
    document está em scielo_classic_website.models.document.Document.
    """
    calls = (
        convert_html_to_xml_step_0_insert_html_in_cdata,
        convert_html_to_xml_step_1_remove_cdata,
        convert_html_to_xml_step_1_embed_html,
        convert_html_to_xml_step_2_html_to_xml,
        convert_html_to_xml_step_2_b,
        convert_html_to_xml_step_2_c,
        convert_html_to_xml_step_3,
        convert_html_to_xml_step_4,
        convert_html_to_xml_step_fix_body,
        convert_html_to_xml_complete_disp_formula,
        # convert_html_to_xml_step_5,
        # convert_html_to_xml_step_6,
        # convert_html_to_xml_step_7,
    )
    document.exceptions = []
    document.xml_body_and_back = []
    for i, call_ in enumerate(calls, start=1):
        try:
            document.xml_body_and_back.append(call_(document))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.info(f"Convert HTML to XML - step {i} failed")
            logging.exception(e)
            document.exceptions.append(
                {
                    "index": i,
                    "error_type": str(type(e)),
                    "error_message": str(e),
                    "exc_traceback": traceback.format_exc(),
                }
            )


def convert_html_to_xml_step_0_insert_html_in_cdata(document):
    """
    Prepara o documento para conversão inserindo conteúdo HTML em estruturas CDATA.

    Insere o HTML principal e traduções dentro de tags CDATA na estrutura XML,
    preparando o documento para as etapas subsequentes de conversão.

    Parameters
    ----------
    document : Document
        Documento contendo HTML a ser convertido para XML

    Returns
    -------
    Document
        Documento com HTML encapsulado em CDATA dentro da estrutura XML
    """
    # logging.info("convert_html_to_xml - step 0")
    ppl = plumber.Pipeline(
        SetupPipe(),
        PreMainHTMLPipe(),
        PreTranslatedHTMLPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_1_remove_cdata(document):
    """
    Remove as tags CDATA e posiciona o conteúdo HTML na estrutura XML.

    Posiciona os textos HTML principal e traduções na estrutura do XML:
    - article/body
    - article/back/ref-list
    - article/back/sec
    - sub-article/body
    - sub-article/back

    Parameters
    ----------
    document : Document
        Documento com HTML em CDATA

    Returns
    -------
    Document
        Documento com HTML integrado à estrutura XML sem CDATA
    """
    # logging.info("convert_html_to_xml - step 1")
    ppl = plumber.Pipeline(
        StartPipe(),
        MainHTMLPipe(),
        TranslatedHTMLPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_1_embed_html(document):
    ppl = plumber.Pipeline(
        StartPipe(),
        MarkHTMLFileToEmbedPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_2(document):
    # SEM USO, SUBSTITUIDO POR 2_a, 2_b e 2_c
    """
    Converte o XML obtido no passo 1,
    converte as tags HTML nas XML correspondentes
    sem preocupação em manter a hierarquia exigida no XML

    Parameters
    ----------
    document: Document

    ((address | alternatives | answer | answer-set | array |
    block-alternatives | boxed-text | chem-struct-wrap | code | explanation |
    fig | fig-group | graphic | media | preformat | question | question-wrap |
    question-wrap-group | supplementary-material | table-wrap |
    table-wrap-group | disp-formula | disp-formula-group | def-list | list |
    tex-math | mml:math | p | related-article | related-object | disp-quote |
    speech | statement | verse-group)*, (sec)*, sig-block?)
    """
    # logging.info("convert_html_to_xml - step 2")
    ppl = plumber.Pipeline(
        StartPipe(),
        XMLNormalizeSpacePipe(),
        # RemoveCDATAPipe(),
        RemoveCommentPipe(),
        FontSymbolPipe(),
        FixMissingParagraphsPipe(),
        ReplaceBrByPPipe(),
        CreateStyleTagFromAttributePipe(),
        RemoveHTMLTagsPipe(),
        RenameElementsPipe(),
        StylePipe(),
        RemoveSpanTagsPipe(),
        ReplaceBrByPPipe(),
        OlPipe(),
        UlPipe(),
        TagsHPipe(),
        ASourcePipe(),
        ANamePipe(),
        AHrefPipe(),
        ImgSrcPipe(),
        RemoveEmptyPTagPipe(),
        RemoveEmptyRefTagPipe(),
        RemoveExcedingBreakTagPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_2_html_to_xml(document):
    """
    Primeira etapa de conversão de tags HTML para XML correspondentes.

    Realiza conversões básicas de elementos HTML:
    - Normaliza espaços em branco
    - Remove comentários HTML
    - Converte símbolos de fonte especiais
    - Renomeia elementos HTML para tags XML apropriadas (div→sec, b→bold, etc.)
    - Processa listas ordenadas (ol) e não ordenadas (ul)
    - Converte tags de cabeçalho (h1-h6) em títulos
    - Cria tags de estilo (bold, italic, sup, sub) a partir de atributos
    - Processa elementos de estilo inline

    Parameters
    ----------
    document : Document
        Documento com HTML integrado na estrutura XML

    Returns
    -------
    Document
        Documento com tags HTML parcialmente convertidas para XML
    """
    # logging.info("convert_html_to_xml - step 2_a")
    ppl = plumber.Pipeline(
        StartPipe(),
        XMLNormalizeSpacePipe(),
        RemoveCommentPipe(),
        FontSymbolPipe(),
        RenameElementsPipe(),
        OlPipe(),
        UlPipe(),
        TagsHPipe(),
        CreateStyleTagFromAttributePipe(),
        StylePipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_2_b(document):
    """
    Segunda etapa de conversão focada em estrutura de parágrafos e formatação.

    Processa elementos de formatação e estrutura:
    - Converte atributos 'size' em tags apropriadas (bold, title)
    - Corrige estrutura de parágrafos e quebras de linha

    Parameters
    ----------
    document : Document
        Documento processado pela etapa 2_a

    Returns
    -------
    Document
        Documento com estrutura de parágrafos corrigida
    """
    # logging.info("convert_html_to_xml - step 2_b")
    ppl = plumber.Pipeline(
        StartPipe(),
        SizeAttributePipe(),
        FixParagraphsAndBreaksPipe(),
        RemoveHTMLTagsPipe(),
        RemoveSpanTagsPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_2_c(document):
    """
    Terceira etapa de conversão focada em processamento de links.

    Processa elementos de hiperlink:
    - Converte atributos href em estruturas XML apropriadas
    - Processa âncoras e links internos

    Parameters
    ----------
    document : Document
        Documento processado pela etapa 2_b

    Returns
    -------
    Document
        Documento com links processados
    """
    # logging.info("convert_html_to_xml - step 2_c")
    ppl = plumber.Pipeline(
        StartPipe(),
        ASourcePipe(),
        ImgSrcPipe(),
        AHrefPipe(),
        XRefAssetTypeImagePipe(),
        XRefAssetOtherTypesPipe(),
        XRefPipe(),
        ANamePipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_3(document):
    """
    Processa referências cruzadas e gráficos inline.

    Identifica e processa elementos de referência:
    - Localiza e processa tags xref adicionando atributo ref-type
    - Processa gráficos inline
    - Identifica links internos especiais

    Parameters
    ----------
    document : Document
        Documento processado pela etapa 2_c

    Returns
    -------
    Document
        Documento com referências cruzadas e gráficos inline processados
    """
    # logging.info("convert_html_to_xml - step 3")
    ppl = plumber.Pipeline(
        StartPipe(),
        InlineGraphicPipe(),
        # RemoveParentPTagOfGraphicPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_4(document):
    """
    Organiza elementos de figuras, tabelas e fórmulas.

    Estrutura elementos complexos:
    - Substitui atributos idhref e ridhref por id
    - Converte divs com id para elementos de asset apropriados
    - Define tipos de xref
    - Insere gráficos em elementos fig
    - Insere gráficos em elementos table-wrap
    - Remove tags vazias

    Parameters
    ----------
    document : Document
        Documento processado pela etapa 3

    Returns
    -------
    Document
        Documento com figuras, tabelas e fórmulas estruturadas
    """
    # logging.info("convert_html_to_xml - step 4")
    ppl = plumber.Pipeline(
        StartPipe(),
        InsertGraphicInFigPipe(),
        RemoveEmptyTagPipe(),
        InsertGraphicInTableWrapPipe(),
        RemoveEmptyTagPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_5(document):
    """
    Adiciona legendas e títulos em tabelas.

    Completa a estrutura de tabelas:
    - Insere elementos caption e title em table-wrap
    - Organiza a hierarquia de elementos de tabela

    Parameters
    ----------
    document : Document
        Documento processado pela etapa 4

    Returns
    -------
    Document
        Documento com estrutura de tabelas completa
    """
    # logging.info("convert_html_to_xml - step 5")
    ppl = plumber.Pipeline(
        StartPipe(),
        InsertCaptionAndTitleInTableWrapPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_7(document):
    """
    Processa elementos alternativos de gráficos.

    Cria estruturas de alternatives para gráficos:
    - Agrupa versões alternativas de gráficos
    - Organiza elementos graphic dentro de alternatives

    Parameters
    ----------
    document : Document
        Documento processado pela etapa 5

    Returns
    -------
    Document
        Documento com estruturas alternatives para gráficos
    """
    # logging.info("convert_html_to_xml - step 7")
    ppl = plumber.Pipeline(
        StartPipe(),
        AlternativesGraphicPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_fix_body(document):
    """
    Corrige a estrutura do body envolvendo parágrafos soltos em seções.

    Organiza o conteúdo do body:
    - Envolve parágrafos soltos em elementos sec
    - Garante hierarquia correta do body

    Parameters
    ----------
    document : Document
        Documento com body a ser corrigido

    Returns
    -------
    Document
        Documento com estrutura do body corrigida
    """
    # logging.info("convert_html_to_xml - fix body")
    ppl = plumber.Pipeline(
        StartPipe(),
        WrapPwithSecPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_complete_disp_formula(document):
    """
    Completa a estrutura de fórmulas exibidas (display formulas).

    Finaliza elementos de fórmulas matemáticas:
    - Completa estrutura de disp-formula
    - Adiciona atributos necessários
    - Organiza conteúdo matemático

    Parameters
    ----------
    document : Document
        Documento com fórmulas a serem completadas

    Returns
    -------
    Document
        Documento com estrutura de fórmulas completa
    """
    # logging.info("convert_html_to_xml - complete disp formula")
    ppl = plumber.Pipeline(
        StartPipe(),
        CompleteDispFormulaPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def _process(xml, tag, func):
    nodes = xml.xpath(".//%s" % tag)
    for node in nodes:
        func(node)


def _process_with_params(xml, tag, func, params):
    nodes = xml.xpath(".//%s" % tag)
    for node in nodes:
        func(node, xml, params)


class StartPipe(plumber.Pipe):
    """
    raw.xml_body_and_back é o atributo que guarda os resultados
    de cada conversão do HTML para o XML

    Esta etapa pega o resultado da última conversão feita
    e aplica novas conversões
    """

    def precond(data):
        raw = data
        try:
            if not raw.xml_body_and_back:
                raise plumber.UnmetPrecondition()
        except AttributeError:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw = data
        xml = ET.fromstring(raw.xml_body_and_back[-1])
        _report(xml, func_name=type(self))
        return data, xml


class SetupPipe(plumber.Pipe):
    def transform(self, data):
        nsmap = {
            "xml": "http://www.w3.org/XML/1998/namespace",
            "xlink": "http://www.w3.org/1999/xlink",
        }

        xml = ET.Element("article", nsmap=nsmap)
        _report(xml, func_name=type(self))
        return data, xml


class EndPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        data = ET.tostring(
            xml,
            encoding="utf-8",
            method="xml",
            pretty_print=raw.pretty_print,
        ).decode("utf-8")

        return data


class MainHTMLPipe(plumber.Pipe):
    """
    O texto completo principal é dividido em 3 partes
    - 'before references': antes das referências bibliográficas
    - 'references': referências bibliográficas
    - 'after references': após das referências bibliográficas

    Esta etapa espera que exista `raw.main_html_paragraphs` que é
    um dict com chaves: `before references`, `references`, `after references`.
    Os valores de `before references`, `references`, `after references`
    são listas de dict com chaves text, index, reference_index, part.

    A partir do raw.main_html_paragraphs, são preenchidos os elementos
    article/body, article/back e article/ref-list
    """

    def _process_before_references(self, raw, xml):
        node = xml.find(".//temp[@type='body']")
        if node is not None:
            body = text_to_node("body", node.text)
            xml.find(".").insert(0, body)
            parent = node.getparent()

    def _process_after_references(self, raw, xml):
        node = xml.find(".//temp[@type='back']")
        if node is not None:
            back = text_to_node("back", node.text)
            xml.find(".").insert(1, back)
            parent = node.getparent()

    def transform(self, data):
        """
        Método principal que orquestra a transformação do documento.

        Args:
            data: Tupla contendo (raw, xml)

        Returns:
            data: Tupla processada (raw, xml)
        """
        raw, xml = data

        # Processa cada seção do documento
        self._process_before_references(raw, xml)
        self._process_after_references(raw, xml)

        ref_list_node = xml.find(".//ref-list")
        if ref_list_node is not None:
            back = xml.find(".//back")
            if back is None:
                back = ET.Element("back")
                xml.find(".").append(back)
            back = xml.find(".//back")
            back.insert(0, ref_list_node)

        for item in xml.xpath(".//temp[@type='mixed-citation']"):
            parent = item.getparent()
            new_node = text_to_node("mixed-citation", item.text)
            parent.replace(item, new_node)
        return data


class TranslatedHTMLPipe(plumber.Pipe):
    """
    Esta etapa espera que exista o dict `raw.translated_html_by_lang`
    cujas chaves são os idiomas e os valores são os textos

    O texto completo das traduções é um dicionário composto por dois items:
    - 'before references': texto antes das referências bibliográficas
    - 'after references': texto após as referências bibliográficas

    A partir de cada translated_html_by_lang é gerado um sub-article do tipo
    translation com os elementos body e back
    """

    def transform(self, data):
        raw, xml = data

        article = xml.find(".")
        idx = 0
        for sub_article in xml.xpath(".//sub-article"):

            # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
            # acusará erro de má formação do XML. O conteúdo do CDATA será
            # tratado em uma etapa futura

            temp_body = sub_article.find(".//temp[@type='body']")
            if temp_body is not None:
                try:
                    body = text_to_node("body", temp_body.text)
                    sub_article.append(body)
                except KeyError:
                    pass
            temp_back = sub_article.find(".//temp[@type='back']")
            if temp_back is not None:
                try:
                    back = text_to_node("back", temp_back.text)
                    sub_article.append(back)
                except KeyError:
                    pass

        for item in xml.xpath(".//temp[@type]"):
            parent = item.getparent()
            parent.remove(item)

        return data


##############################################################################


def remove_CDATA(old):
    logging.info(f"Remove CDATA {old.text}")
    # FIXME html_body_tree não definido
    new = html_body_tree(old.text)
    if new:
        new.tag = old.tag
        for name, value in old.attrib.items():
            new.set(name, value)
        parent = old.getparent()
        parent.replace(old, new)


class RemoveCDATAPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for item in xml.findall(".//*"):
            if not item.getchildren() and item.text:
                remove_CDATA(item)
        return raw, xml


class RemoveCommentPipe(plumber.Pipe):
    """
    Remove comentário de HTML.
    <!-- comentario -->
    """

    def transform(self, data):
        raw, xml = data
        comments = xml.xpath("//comment()")
        for comment in comments:
            parent = comment.getparent()
            if parent is not None:
                # isso evita remover comment.tail
                comment.addnext(ET.Element("REMOVE_COMMENT"))
                parent.remove(comment)
        ET.strip_tags(xml, "REMOVE_COMMENT")
        _report(xml, func_name=type(self))
        return data


class RemoveHTMLTagsPipe(plumber.Pipe):
    TAGS = ["font", "small", "big", "s", "lixo", "center"]

    def transform(self, data):
        raw, xml = data
        ET.strip_tags(xml, self.TAGS)
        _report(xml, func_name=type(self))
        return data


class RemoveSpanTagsPipe(plumber.Pipe):
    TAGS = [
        "span",
    ]

    def transform(self, data):
        raw, xml = data
        ET.strip_tags(xml, self.TAGS)
        _report(xml, func_name=type(self))
        return data


##############################################################################
# Rename


class RenameElementsPipe(plumber.Pipe):
    from_to = (
        ("div", "sec"),
        ("dir", "ul"),
        ("dl", "def-list"),
        ("dd", "def-item"),
        ("li", "list-item"),
        ("br", "break"),
        ("blockquote", "disp-quote"),
        ("b", "bold"),
        ("em", "bold"),
        ("i", "italic"),
    )

    def transform(self, data):
        raw, xml = data

        for old, new in self.from_to:
            xpath = f".//{old}"
            for node in xml.findall(xpath):
                node.tag = new
        _report(xml, func_name=type(self))
        return data


class FixParagraphsAndBreaksPipe(plumber.Pipe):

    def fix_paragraphs_and_breaks(self, parent):
        if parent.xpath(".//p"):
            # TODO - casos que há p já existem
            return
        self.fix_paragraph_absence(parent)

    def fix_paragraph_absence(self, parent):
        # troca break duplo por DOUBLEBREAK
        self.mark_double_breaks(parent)
        self.replace_span_followed_by_break_by_p(parent)
        self.replace_span_which_only_child_is_doublebreak_with_p(parent)
        self.replace_font_followed_by_break_by_p_or_sec(parent)

    def mark_double_breaks(self, parent):
        # remove break duplo, substitui por DOUBLEBREAK
        for break_node in parent.xpath(
            "//break[following-sibling::node()[1][self::break]]"
        ):
            if (break_node.tail or "").strip():
                continue
            next_sibling = break_node.getnext()
            if next_sibling.tail and next_sibling.tail.strip():
                continue
            break_node.tag = "DOUBLEBREAK"
            next_sibling.tag = "TOREMOVE"
        ET.strip_tags(parent, "TOREMOVE")

    def replace_span_followed_by_break_by_p(self, parent):
        for span_node in parent.xpath(
            "//span[following-sibling::node()[1][self::DOUBLEBREAK]]"
        ):
            if (span_node.tail or "").strip():
                continue
            span_node.tag = "p"
            next_sibling = span_node.getnext()
            next_sibling.tag = "TOREMOVE"
        ET.strip_tags(parent, "TOREMOVE")

    def replace_span_which_only_child_is_doublebreak_with_p(self, parent):
        # substitui span cujo único filho é doublebreak por p, remove doublebreak
        for node in parent.xpath(".//span[DOUBLEBREAK]"):
            children = node.xpath(".//*")
            if len(children) != 1:
                continue
            child = children[0]
            if (child.tail or "").strip():
                continue
            node.tag = "p"
            child.tag = "BREAKTOREMOVE"
        ET.strip_tags(parent, "BREAKTOREMOVE")

    def replace_font_followed_by_break_by_p_or_sec(self, parent):
        for font_node in parent.xpath(
            "//font[following-sibling::node()[1][self::DOUBLEBREAK]]"
        ):
            if (font_node.tail or "").strip():
                continue
            if font_node.find("p") is None:
                font_node.tag = "p"
            else:
                font_node.tag = "sec"
            next_sibling = font_node.getnext()
            next_sibling.tag = "TOREMOVE"
        ET.strip_tags(parent, "TOREMOVE")

    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            self.fix_paragraphs_and_breaks(body)

        for back in xml.xpath(".//back"):
            self.fix_paragraphs_and_breaks(back)
        return data


class FixMissingParagraphsPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            if body.xpath(".//p"):
                continue
            for child in body.getchildren():
                child.tag = "p"
        return data


class ReplaceBrByPPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            self.replace_tag_by_p(body, "br")
            self.replace_tag_by_p(body, "break")
        return data

    def replace_tag_by_p(self, body, break_tag):
        """Converte elementos com múltiplas tags break em parágrafos separados."""
        for parent_element in body.xpath(f"*[{break_tag}]"):
            break_count = len(parent_element.xpath(break_tag))
            if break_count <= 1:
                continue

            paragraphs = self._split_content_by_breaks(parent_element, break_tag)
            self._replace_with_paragraphs(parent_element, paragraphs)

    def _split_content_by_breaks(self, element, break_tag):
        """Divide o conteúdo de um elemento em segmentos separados por breaks."""
        paragraphs = []
        current_paragraph = ET.Element("p")

        # Adiciona texto inicial do elemento
        if element.text and element.text.strip():
            current_paragraph.text = element.text

        # Processa cada filho do elemento
        for child in list(element):  # list() evita modificação durante iteração
            if child.tag == break_tag:
                # Finaliza parágrafo atual se tiver conteúdo
                if self._has_content(current_paragraph):
                    paragraphs.append(current_paragraph)

                # Inicia novo parágrafo com texto após o break
                current_paragraph = ET.Element("p")
                if child.tail and child.tail.strip():
                    current_paragraph.text = child.tail
            else:
                # Adiciona elemento não-break ao parágrafo atual
                current_paragraph.append(child)

        # Adiciona último parágrafo se tiver conteúdo
        if self._has_content(current_paragraph):
            paragraphs.append(current_paragraph)

        return paragraphs

    def _has_content(self, element):
        """Verifica se um elemento tem conteúdo (texto ou filhos)."""
        return (element.text and element.text.strip()) or len(element) > 0

    def _replace_with_paragraphs(self, original_element, paragraphs):
        """Substitui o elemento original pelos novos parágrafos."""
        # Insere novos parágrafos antes do elemento original
        for paragraph in paragraphs:
            original_element.addprevious(paragraph)

        # Remove o elemento original
        parent = original_element.getparent()
        if parent is not None:
            parent.remove(original_element)


class FontSymbolPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        xpath = f".//font"
        for node in xml.xpath(xpath):
            face = node.get("face")
            if face and "SYMBOL" in face.upper():
                node.tag = "font-face-symbol"
        _report(xml, func_name=type(self))
        return data


class CreateStyleTagFromAttributePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for node in xml.xpath(".//*[@style]"):
            for style in ("italic", "sup", "sub", "bold", "underline"):
                if style in node.get("style"):
                    node.tag = style
                    break
        return data


class SizeAttributePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for node in xml.xpath(".//*[@size]"):
            size = node.get("size")
            if size[0] == "-":
                continue
            s = size
            if s[0] == "+":
                s = s[1:]
            try:
                if int(s) > 1:
                    node.tag = "title"
            except (ValueError, TypeError):
                pass
        return data


class StylePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for style in ("bold", "italic", "sup", "sub", "underline"):
            xpath = f".//span[@name='style_{style}']"
            for node in xml.xpath(xpath):
                node.tag = style
                node.attrib.pop("name")
        _report(xml, func_name=type(self))
        return data


class OlPipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "list"
        node.set("list-type", "order")

    def transform(self, data):
        raw, xml = data
        _process(xml, "ol", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class UlPipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "list"
        node.set("list-type", "bullet")
        node.attrib.pop("list", None)

    def transform(self, data):
        raw, xml = data
        _process(xml, "ul", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class TagsHPipe(plumber.Pipe):
    def parser_node(self, node):
        node.attrib.clear()
        org_tag = node.tag
        node.tag = "title"
        node.set("content-type", org_tag)

    def transform(self, data):
        raw, xml = data
        tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
        for tag in tags:
            _process(xml, tag, self.parser_node)
        _report(xml, func_name=type(self))
        return data


class ASourcePipe(plumber.Pipe):
    def _change_src_to_href(self, node):
        href = node.attrib.get("href")
        src = node.attrib.get("src")
        if not href and src:
            node.attrib["href"] = node.attrib.pop("src")

    def transform(self, data):
        raw, xml = data
        _process(xml, "a[@src]", self._change_src_to_href)
        _report(xml, func_name=type(self))
        return data


##############################################################################


class AHrefPipe(plumber.Pipe):
    """
    Pipe para processar tags <a> em documentos XML, convertendo-as para formato SPS.

    Este pipe transforma elementos <a> do HTML em elementos apropriados do padrão SPS XML:
    - Links de email (<a href="mailto:...">) → <email>
    - Links internos (<a href="#id">) → <xref rid="id">
    - Links para arquivos locais → <xref> com metadados de asset (tipo, mimetype, etc.)
    - Links externos → <ext-link>

    O pipe identifica automaticamente o tipo de link baseado no valor do atributo href
    e aplica a transformação apropriada, incluindo:
    - Detecção de arquivos locais por padrão de caminho
    - Classificação de assets por extensão (pdf, imagem, vídeo, áudio, etc.)
    - Adição de metadados de tipo MIME
    - Sanitização de valores href malformados

    Attributes:
        Herda de plumber.Pipe

    Methods:
        transform(data): Processa todos os elementos <a> no XML
        parser_node(node, journal_acron, journal_acron_folder): Analisa e transforma um nó <a>
        sanitize_href(node): Remove caracteres inválidos do atributo href
        _is_local_file(href, journal_acron_folder): Verifica se href aponta para arquivo local
        _create_ext_link(node, extlinktype): Converte para <ext-link>
        _create_email(node): Converte para <email>
        _create_internal_link(node): Converte para <xref> interno
        _create_internal_link_for_asset(node): Converte para <xref> de asset com metadados
    """

    def _is_local_file(self, href: str, journal_acron_folder) -> bool:
        """
        Determina se um arquivo HTML é local baseado na presença de acrônimo entre barras.

        Args:
            href: Caminho para o arquivo HTML

        Returns:
            True se for arquivo local (contém /acrônimo/), False caso contrário
        """
        # Normaliza barras
        normalized_href = href.replace("\\", "/")

        if journal_acron_folder not in normalized_href:
            return False

        # URLs absolutas não são locais
        if normalized_href.startswith("http://") or normalized_href.startswith(
            "https://"
        ):
            return False

        # Verifica padrão /acrônimo/ no caminho
        pattern = r".*/([a-zA-Z]+)/[^/]*\.[^/]+(?:#.*)?$"
        return bool(re.search(pattern, normalized_href))

    def _create_ext_link(self, node, extlinktype="uri"):
        node.tag = "ext-link"
        href = (node.get("href") or "").strip()
        node.attrib.clear()
        node.set("ext-link-type", extlinktype)
        node.set("{http://www.w3.org/1999/xlink}href", href)

    def _create_email(self, node):
        node.tag = "email"
        href = (node.get("href") or "").strip()
        node.attrib.clear()

        texts = href.replace("mailto:", "")
        for text in texts.split():
            if "@" in text:
                node.text = text
                return

        texts = " ".join(node.xpath(".//text()")).strip()
        for text in texts.split():
            if "@" in text:
                node.text = text
                return

    def _create_internal_link(self, node):
        try:
            href = node.get("href").strip()
            rid = href.lstrip("#")
            if "top" in rid or "back" in rid:
                node.set("delete", "true")
                # nota: não remover o a[@name='top' or @name='back'] porque podem ter conteúdo
                return
            node.attrib.clear()
            node.tag = "xref"
            node.set("rid", rid)
        except (ValueError, TypeError, AttributeError, IndexError) as e:
            xml = ET.tostring(node)
            logging.error(f"Unable to _create_internal_link for {xml}")
            logging.exception(e)

    def _create_internal_link_for_asset(self, node):
        node.tag = "xref"
        href_parts = node.get("href").split("#")
        path = href_parts[0]
        name, ext = os.path.splitext(os.path.basename(path))
        node.set("path", path)
        node.set("rid", name)
        ext = ext.lower()
        asset_type = "other"
        mimetype = None
        mime_subtype = None
        
        config = ASSET_TYPE_CONFIG.get(ext)
        if config:
            asset_type = config["asset_type"]
            mimetype = config["mimetype"]
            mime_subtype = config["mime_subtype"]
            if ext in (".htm", ".html") and len(href_parts) > 1:
                node.set("anchor", href_parts[1])

        node.set("asset_type", asset_type)
        if mimetype:
            node.set("mimetype", mimetype)
        if mime_subtype:
            node.set("mime-subtype", mime_subtype)

    def parser_node(self, node, journal_acron, journal_acron_folder):
        href = self.sanitize_href(node)
        if not href:
            return
        text = " ".join(node.xpath(".//text()")).strip()
        if ("mailto" in href) or ("@" in href) or (text and "@" in text):
            # email
            return self._create_email(node)

        if href[0] == "#":
            # xref interno
            return self._create_internal_link(node)

        if self._is_local_file(href, journal_acron or ""):
            # xref para asset interno
            return self._create_internal_link_for_asset(node)

        if journal_acron_folder and journal_acron_folder in href.lower():
            # xref para asset interno
            return self._create_internal_link_for_asset(node)

        if "img/revistas/" in href or ".." in href:
            # xref para asset interno
            return self._create_internal_link_for_asset(node)

        if ":" in href:
            # ext-link
            return self._create_ext_link(node)
        if "www" in href:
            # ext-link
            return self._create_ext_link(node)
        if href.startswith("http"):
            # ext-link
            return self._create_ext_link(node)
        href = href.split("/")[0]
        if href and href.count(".") and href.replace(".", ""):
            # ext-link
            return self._create_ext_link(node)

    def sanitize_href(self, node):
        href = (node.get("href") or "").strip()
        if href.count('"') == 2:
            href = href.replace('"', "")
            node.set("href", href)
        return href

    def transform(self, data):
        raw, xml = data
        journal_acron = raw.journal and raw.journal.acronym
        journal_acron_folder = f"/{journal_acron}/" if journal_acron else ""
        for node in xml.xpath(".//a[@href]"):
            self.parser_node(node, journal_acron, journal_acron_folder)
        delete_tags(xml)
        return data


class ANamePipe(plumber.Pipe):
    """
    Pipe para processar tags <a name="..."> em documentos XML:
    - Remoção de âncoras especiais 'top' e 'back' quando vazias
    - Eliminação de âncoras duplicadas (múltiplas ocorrências do mesmo 'name')
    - Conversão de <a name="id"> para elemento genérico com atributo id
    """

    def remove_top_and_back(self, root):
        for node in root.xpath(".//a[@name]"):
            name = node.get("name")
            if name.startswith("top") or name.startswith("back"):
                node.set("id", name)
                if (node.tail or "").strip():
                    continue
                if node.getchildren():
                    continue
                text = " ".join(node.xpath(".//text()")).strip()
                if text:
                    continue
                node.set("delete", "true")
        delete_tags(root)

    def remove_multiplicity(self, root):
        items = []
        for node in root.xpath(".//a[@name]"):
            name = node.get("name")
            if name in items:
                node.set("delete", "true")
            else:
                items.append(name)
        delete_tags(root)

    def transform(self, data):
        raw, xml = data
        self.remove_top_and_back(xml)
        self.remove_multiplicity(xml)
        for node in xml.xpath(".//a[@name]"):
            node.tag = "element"
            node.set("id", node.attrib.pop("name"))
        return data


class ImgSrcPipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "graphic"
        href = node.attrib.pop("src")
        node.attrib.clear()
        node.set("{http://www.w3.org/1999/xlink}href", href)

    def transform(self, data):
        raw, xml = data
        _process(xml, "img[@src]", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class XRefPipe(plumber.Pipe):
    """
    Processa elementos xref, identificando e configurando ref-type apropriado
    e atualizando tags de elementos referenciados e
    atributo 'name' é substituído por 'id'

    Exemplos de transformações:
    - <xref rid="fn1">Footnote 1</xref> → adiciona ref-type="fn"
    - <xref rid="aff01">Author affiliation</xref> → adiciona ref-type="aff"
    - <xref rid="B1">Reference 1</xref> → adiciona ref-type="bibr"
    - <xref rid="corresp">*</xref> → adiciona ref-type="corresp"

    Atualiza tags e atributos de elementos referenciados:
    - <a name="fn1">...</a> → <fn id="fn1">...</fn>
    - <a name="aff01">...</a> → <aff id="aff01">...</aff>

    """

    def add_reftype(self, node, xml):
        rid = node.get("rid")
        if not rid:
            return
        text = " ".join(node.xpath(".//text()")).strip()
        if not text:
            return
        if "corresp" in rid:
            result = {"ref_type": "corresp", "element_name": "corresp"}
        else:
            result = analyze_xref(text, rid)
        if ref_type := result.get("ref_type"):
            node.set("ref-type", ref_type)
        element_name = result.get("element_name")
        if element_name:
            for elem in xml.xpath(f".//*[@name='{rid}']"):
                elem.tag = element_name
                elem.set("id", rid)
                elem.attrib.pop("name", None)

    def handle_special_xref_reftypes(self, xml, ref_type):
        xrefs = xml.xpath(f".//xref[@ref-type='{ref_type}']")
        if not xrefs:
            return
        for xref in xrefs:
            self.discover_reftype_and_element_name(xml, xref)

    def discover_reftype_and_element_name(self, xml, xref):
        rid = xref.get("rid")
        node_ref_type = None
        if xref.get("ref-type") == "number":
            items = (
                (".//ref-list", "ref", "bibr"),
                (".//back", "fn", "fn"),
                (".//body", "aff", "aff"),
            )
        else:
            items = (
                (".//back", "fn", "fn"),
                (".//body", "aff", "aff"),
            )
        for xpath, tag, reftype in items:
            for root in xml.xpath(xpath):
                for elem in root.xpath(f".//*[@name='{rid}']"):
                    elem.tag = tag
                    elem.set("id", rid)
                    elem.attrib.pop("name", None)
                    node_ref_type = reftype
                    break
            if node_ref_type:
                xref.set("ref-type", node_ref_type)
                return

    def transform(self, data):
        raw, xml = data
        for xref in xml.xpath(".//xref[not(@ref-type)]"):
            self.add_reftype(xref, xml)
        self.handle_special_xref_reftypes(xml, "number")
        self.handle_special_xref_reftypes(xml, "symbol")
        self.handle_special_xref_reftypes(xml, "letter")
        return data


class XRefAssetTypeImagePipe(plumber.Pipe):
    """
    Processa xrefs do tipo asset_type='image'.
    Cria elementos (fig, table-wrap, disp-formula, ...) a partir dos xrefs do tipo image.
    """

    def transform(self, data):
        raw, xml = data
        if not xml.xpath(".//xref[@asset_type='image']"):
            return data
        self.find_parents(xml)
        for xref_parent in xml.xpath(".//*[@xref-parent='true']"):
            self.process_parent(raw, xml, xref_parent)
        _report(xml, func_name=type(self))
        return data

    def find_parents(self, xml):
        for xref in xml.xpath(".//xref[@asset_type='image']"):
            parent = xref.getparent()
            parent.set("xref-parent", "true")

    def process_parent(self, raw, xml, xref_parent):
        new_elements = self.get_elements_to_create(
            xref_parent,
            xml,
            raw.filename_without_extension,
        )
        for new_element in new_elements:
            node = ET.Element("p")
            node.append(new_element)
            xref_parent.addnext(node)

    def _extract_xref_text(self, xref_element):
        return " ".join(xref_element.xpath(".//text()")).strip()

    def get_label_text_and_number_from_xref_text(self, xref_text, previous_label_text):
        # Tables 1-3
        if not xref_text:
            return None, None

        parts = xref_text.split()

        # first character of last part
        expected_number = parts[-1]
        if expected_number[0].isdigit():
            if len(parts) == 2:
                return parts[0], expected_number
            if len(parts) == 1:
                return previous_label_text, expected_number
        return parts[0], None

    def get_elements_to_create(self, xref_parent, xml, pkg_name):
        label_text = None
        children = []

        # navega pelos xref dentro do xref_parent
        # trata casos como <xref>Table 1</xref> and <xref>2</xref>
        for child in xref_parent.xpath("xref[@asset_type='image' and @path]"):
            # guarda label_text anterior (Table)
            previous_label_text = label_text
            # Table 1
            xref_text = self._extract_xref_text(child)
            if not xref_text:
                logging.error("XRefAssetTypeImagePipe - no xref_text found")
                continue
            label_text, label_number = self.get_label_text_and_number_from_xref_text(
                xref_text, previous_label_text
            )
            label = " ".join(
                [
                    item.strip()
                    for item in [label_text, label_number]
                    if item and item.strip()
                ]
            )
            if not label:
                logging.error("XRefAssetTypeImagePipe - no label found")
                continue
            ref_type, element_name, prefix, number = detect_from_text(label)
            if ref_type:
                child.set("ref-type", ref_type)

            # verifica se já existe o elemento referenciado por xref
            # cria se não existir e completa os atributos
            path = child.get("path")
            rid = child.get("rid")
            xpath = f"//*[@id='{rid}' or @name='{rid}' or @path='{path}']"

            try:
                element = xml.xpath(xpath)[0]
                element.set("id", rid)
            except IndexError:
                new_elem = ET.Element(element_name)
                new_elem.set("id", rid)
                new_elem.set("path", path)

                elem_label = ET.Element("label")
                new_elem.append(elem_label)
                elem_label.text = label

                g = ET.Element("graphic")
                g.set("{http://www.w3.org/1999/xlink}href", path)

                new_elem.append(g)
                children.append(new_elem)

            child.attrib.pop("asset_type")

        if not children:
            return []

        # Sort children by rid before inserting
        return reversed(sorted(children, key=lambda x: x.get("id")))


class InsertGraphicInFigPipe(plumber.Pipe):
    """
    Envolve o elemento graphic dentro de fig.

    Resultado esperado:

    <fig id="f1">
        <graphic xlink:href="f1.jpg"/>
    </fig>
    """

    def parser_node(self, node):
        if node.find("table") is not None:
            return
        if node.find("graphic") is not None:
            return

        parent = node.getparent()

        while True:
            grand_parent = parent.getparent()
            if grand_parent is None:
                break
            if grand_parent.tag == "body":
                break
            parent = grand_parent

        sibling = parent.getnext()
        if sibling is None:
            return
        graphic = sibling.find(".//graphic")
        if graphic is None:
            return
        node.append(deepcopy(graphic))
        parent = graphic.getparent()
        parent.remove(graphic)

    def transform(self, data):
        raw, xml = data
        _process(xml, "fig[@id]", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class InsertGraphicInTableWrapPipe(plumber.Pipe):
    """
    Envolve o elemento graphic dentro de table-wrap.

    Antes:

    <p align="center">
        <table-wrap id="t1"/>
    </p>
    <p align="center"> </p>
    <p align="center"><b>Table 1 Composition and energy provide by the experimental diets</b></p>
    <p align="center">
        <graphic xlink:href="t01.jpg"/>
    </p>

    Resultado esperado:

    <table-wrap id="t1">
        <graphic xlink:href="t01.jpg"/>
    </table-wrap>

    Antes:

    <p align="center">
        <table-wrap id="t1"/>
    </p>
    <p align="center"> </p>
    <p align="center"><b>Table 1 Composition and energy provide by the experimental diets</b></p>
    <p align="center">
        <table/>
    </p>

    Depois:

    <table-wrap id="t1">
        <table/>
    </table-wrap>
    """

    def parser_node(self, node):
        if node.find("table") is not None:
            return
        if node.find("graphic") is not None:
            return

        parent = node.getparent()

        while True:
            grand_parent = parent.getparent()
            if grand_parent is None:
                break
            if grand_parent.tag == "body":
                break
            parent = grand_parent

        sibling = parent.getnext()
        if sibling is None:
            comment = ET.Comment("FIXME check whether element is table-wrap")
            node.insert(1, comment)
            logging.info(f"Unable to find graphic for {node.get('id')}")
            return
        table = sibling.find(".//table")
        graphic = sibling.find(".//graphic")
        if graphic is None and table is None:
            return

        elem = None
        if graphic is not None:
            node.append(deepcopy(graphic))
            elem = graphic
        elif table is not None:
            node.append(deepcopy(table))
            elem = table

        if elem is not None:
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

    def transform(self, data):
        raw, xml = data
        _process(xml, "table-wrap[@id]", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class RemoveEmptyTagPipe(plumber.Pipe):
    """
    Remove parágrafo vazio, ou que contenha somente espaços em branco.

    Ex: <p> </p>
    """

    def mark_empty_tag(self, node):
        # Verifica se existe algum filho no node.
        if node.getchildren():
            return None
        # Verifica se node.text tem conteúdo.
        if node.text and node.text.strip():
            return None
        node.tag = "REMOVE_EMPTY_TAG"

    def remove_empty_tags(self, xml, tag):
        for node in xml.findall(f".//{tag}"):
            self.mark_empty_tag(node)
        ET.strip_tags(xml, "REMOVE_EMPTY_TAG")

    def transform(self, data):
        raw, xml = data
        self.remove_empty_tags(xml, "p")
        self.remove_empty_tags(xml, "sec")
        return data


class RemoveEmptyPTagPipe(plumber.Pipe):
    """
    Remove parágrafo vazio, ou que contenha somente espaços em branco.

    Ex: <p> </p>
    """

    def parser_node(self, node):
        # Verifica se existe algum filho no node.
        if len(node.getchildren()):
            return None
        # Verifica se node.text tem conteúdo.
        if node.text and node.text.strip():
            return None

        tail = node.tail
        parent = node.getparent()
        parent.remove(node)

        # Adiciona o tail no parent.
        parent.text = tail

    def transform(self, data):
        raw, xml = data
        _process(xml, "p", self.parser_node)
        _process(xml, "sec", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class RemoveEmptyRefTagPipe(plumber.Pipe):
    """
    Remove parágrafo vazio, ou que contenha somente espaços em branco.

    Ex: <p> </p>
    """

    def transform(self, data):
        raw, xml = data

        for item in xml.xpath(".//ref"):
            text = "".join(item.xpath(".//text()")).strip()
            if not text:
                item.tag = "REMOVE_EMPTY_REF_TAG"
        ET.strip_tags(xml, "REMOVE_EMPTY_REF_TAG")
        return data


class RemoveExcedingBreakTagPipe(plumber.Pipe):
    """
    Remove parágrafo vazio, ou que contenha somente espaços em branco.

    Ex: <p> </p>
    """

    def transform(self, data):
        raw, xml = data

        for parent in xml.xpath(".//p[break]"):
            for item in parent.xpath("break"):
                if (item.tail or "").strip():
                    continue
                if item.getnext() is not None:
                    continue
                item.tag = "REMOVE_EXCEDING_BREAK_TAG"
        ET.strip_tags(xml, "REMOVE_EXCEDING_BREAK_TAG")

        for parent in xml.xpath(".//mixed-citation[break]"):
            for item in parent.xpath("break"):
                item.tag = "REMOVE_EXCEDING_BREAK_TAG"
        ET.strip_tags(xml, "REMOVE_EXCEDING_BREAK_TAG")
        return data


class InlineGraphicPipe(plumber.Pipe):
    """
    Crie um pipe para converter graphic em inline-graphic.
    Estes graphic são aqueles cujo parent tem
    text (parent.text and parent.text.strip() e / ou
    graphic tem tail (graphic.tail and graphic.tail.strip()) e / ou
    nó anterior tem tail(graphic.getprevious() and graphic.getprevious().tail.strip())
    """

    def graphic_to_inline(self, node):
        if node.tag == "graphic":
            g = node
        else:
            g = node.find(".//graphic")
        g.tag = "inline-graphic"

    def parser_node(self, node):
        if node.text and node.text.strip():
            _process(node, "graphic", self.graphic_to_inline)
            return

        has_text = False
        for child in node.getchildren():
            if child.tail and child.tail.strip():
                has_text = True
                break

        if has_text:
            _process(node, "graphic", self.graphic_to_inline)

    def transform(self, data):
        raw, xml = data
        _process(xml, "p[graphic]", self.parser_node)
        _process(xml, "xref[graphic]", self.graphic_to_inline)
        _report(xml, func_name=type(self))
        return data


class RemoveParentPTagOfGraphicPipe(plumber.Pipe):
    """
    Remove parent de graphic se parent.tag == 'p'.

    Antes:

    <p align="center">
      <graphic xlink:href="53t01.jpg"/>
    </p>

    Depois:

    <graphic xlink:href="53t01.jpg"/>
    """

    def parser_node(self, node):
        # Pega o parent do node.
        parent = node.getparent()

        # Pega o primeiro filho do node.
        graphic = node.getchildren()[0]

        # Adiciona o graphic em parent.
        index = parent.index(node)
        parent.insert(index, graphic)

        # Remove o node. <p> com todos os filhos.
        parent.remove(node)

    def transform(self, data):
        raw, xml = data
        _process(xml, "p[graphic]", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class InsertCaptionAndTitleInTableWrapPipe(plumber.Pipe):
    """
    Insere caption dentro de table-wrap.
    E title dentro de caption.
    Pode conter label ou não.
    """

    def process(self, xml, tag, xref_dict, func):
        # Este process passa a tag e uma lista.
        nodes = xml.findall(".//%s" % tag)
        for node in nodes:
            func(node, xref_dict)

    def add_label(self, node, label):
        # cria label / nao há caption
        label_node = ET.Element("label")
        label_node.text = label
        node.insert(0, label_node)

    def find_label_and_caption(self, node, labels):
        """
        <label>Tabela 5</label>
          <caption>
            <title>Alíquota menor para prestadores</title>
          </caption>
        """
        table_id = node.get("id")
        label = labels.get(table_id)
        if not label:
            # table-wrap não tem xref, logo não se sabe o label
            return

        parent = node.getparent()
        if parent is None:
            self.add_label(node, label)
            return

        previous_node = parent.getprevious()
        if previous_node is None:
            self.add_label(node, label)
            return

        # verifica se os textos de previous node contém label (xref content)
        texts = previous_node.xpath(".//text()")
        text = " ".join(texts)
        if text and text.strip().upper().startswith(label.upper()):
            pass
        else:
            self.add_label(node, label)
            return

        # sim, os textos de previous node contém label (xref content)
        # identificar o node que contém o texto do label
        found_label_node = None
        for child in previous_node.xpath(".//*"):
            # procura nos filhos
            if child.text.strip().upper().startswith(label.upper()):
                found_label_node = child
                break
        else:
            # procura no próprio nó
            if previous_node.text and previous_node.text.strip().upper().startswith(
                label.upper()
            ):
                found_label_node = previous_node

        if found_label_node is None:
            # não encontrou
            # pode decidir criar ou não
            self.add_label(node, label)
            return

        # encontrou elemento que contém label
        # precisa identificar se o elemento contém somente label ou label + caption
        found_label_node_text = found_label_node.text.strip()[: len(label)]
        caption_node_text = found_label_node.text.replace(
            found_label_node_text, ""
        ).strip()

        if caption_node_text:
            # elemento contém label + caption
            caption_node = ET.Element("caption")
            title_node = ET.Element("title")
            title_node.text = caption_node_text
            caption_node.append(title_node)
            label_node = ET.Element("label")
            label_node.text = found_label_node_text
            node.append(label_node)
            node.append(caption_node)
        else:
            # elemento contém somente label
            next_node = found_label_node.getnext()
            if next_node is None:
                label_node = deepcopy(found_label_node)
                label_node.tag = "label"
                node.append(label_node)
                return

            title_node = deepcopy(next_node)
            title_node.tag = "title"
            caption_node = ET.Element("caption")
            caption_node.append(title_node)

            label_node = deepcopy(found_label_node)
            label_node.tag = "label"

            node.append(label_node)
            node.append(caption_node)

    def transform(self, data):
        raw, xml = data
        xref_items = xml.xpath(".//xref[@rid and @ref-type='table']")

        labels = {}
        for xref in xref_items:
            # A chave é o id e o valor é o texto.
            # Ex: {'t1': 'Table 1', 't2': 'Table 2'}
            if xref.text:
                labels[xref.attrib["rid"]] = xref.text.strip()

        if labels:
            self.process(xml, "table-wrap[@id]", labels, self.find_label_and_caption)
        _report(xml, func_name=type(self))
        return data


class InsertTableWrapFootInTableWrapPipe(plumber.Pipe):
    """
    Insere table-wrap-foot em table-wrap.
    """

    def parser_node(self, node):
        parent = node.getparent()
        next_node = parent.getnext()
        if next_node is None:
            return

        # FIXME - haver o próximo não é garantia de ser footnote
        # table_wrap_foot = ET.Element("table-wrap-foot")
        # table_wrap_foot.append(next_node)

        # node.append(table_wrap_foot)

    def transform(self, data):
        raw, xml = data
        _process(xml, "table-wrap[@id]", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class AlternativesGraphicPipe(plumber.Pipe):
    """
    Agrupa as imagens miniatura e padrão em alternatives.

    Antes:

    <qualquer-tag>
        <a href="/fbpe/img/bres/v48/53t03.jpg">
          <graphic xlink:href="/fbpe/img/bres/v48/53t03thumb.jpg"/>
        </a>
    </qualquer-tag>

    Depois:

    <qualquer-tag>
        <alternatives>
            <graphic xlink:href="/fbpe/img/bres/v48/53t03.jpg"/> <!-- imagem "original" (tiff), mas na ausência usar a imagem padrão -->
            <graphic xlink:href="/fbpe/img/bres/v48/53t03.jpg" specific-use="scielo-web"/> <!-- imagem "ampliada" ou padrão -->
            <graphic xlink:href="/fbpe/img/bres/v48/53t03thumb.jpg" specific-use="scielo-web" content-type="scielo-267x140"/> <!-- imagem miniatura -->
        </alternatives>
    </qualquer-tag>
    """

    def parser_node(self, node):
        parent = node.getparent()
        _graphic = node.getchildren()[0]

        alternatives = ET.Element("alternatives")

        graphic1 = ET.Element("graphic")
        xlink_ref = "{http://www.w3.org/1999/xlink}href"
        graphic1.set(xlink_ref, node.attrib["href"])
        alternatives.append(graphic1)

        graphic2 = ET.Element("graphic")
        xlink_ref = "{http://www.w3.org/1999/xlink}href"
        graphic2.set(xlink_ref, node.attrib["href"])
        graphic2.set("specific-use", "scielo-web")
        alternatives.append(graphic2)

        graphic_thumb = ET.Element("graphic")
        graphic_thumb.set(
            xlink_ref, _graphic.attrib["{http://www.w3.org/1999/xlink}href"]
        )
        graphic_thumb.set("specific-use", "scielo-web")
        graphic_thumb.set("content-type", "scielo-267x140")
        alternatives.append(graphic_thumb)

        # Troca o node 'a' por 'alternatives'
        # Adicionando 'alternatives'
        parent.append(alternatives)

        # E removendo o node 'a'
        parent.remove(node)

    def transform(self, data):
        raw, xml = data
        _process(xml, "a[graphic]", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class WrapPwithSecPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            self.replace_bold_by_title(body)
            self.fix_sec(body)
            self.complete_ref_list_title(body)
            self.fix_body_begin(body)
        return data

    def replace_bold_by_title(self, body):
        for bold in body.xpath(".//bold"):
            if bold.text is None and len(bold.getchildren()) == 0:
                parent = bold.getparent()
                parent.remove(bold)
        for p_node in body.xpath(f"p[bold]"):
            p_text = "".join(p_node.xpath(".//text()")).strip()
            bold_node = p_node.find(".//bold")
            bold_text = "".join(bold_node.xpath(".//text()")).strip()
            if p_text == bold_text:
                bold_node.tag = "title"
                sec_type = get_sectype(bold_text.lower())
                if sec_type:
                    p_node.set("sec-type", sec_type)
                p_node.tag = "sec"
                if p_node.getchildren()[0].tag != "title":
                    p_node.remove(p_node.getchildren()[0])

    def fix_sec(self, body):
        if body.find("sec") is None:
            return

        sec_node = None
        for body_child in body.getchildren():
            if body_child.tag == "sec":
                sec_node = body_child
                continue

            if sec_node is None:
                sec_node = ET.Element("sec")
                body_child.addprevious(sec_node)

            sec_node.append(body_child)

        for body_child in body.xpath("p"):
            body.remove(body_child)

    def complete_ref_list_title(self, body):
        back = body.getnext()
        if back is None:
            return

        ref_list_node = back.find("ref-list")
        if ref_list_node is None:
            return

        if ref_list_node.find("title") is not None:
            return
        try:
            node = body.getchildren()[-1]
        except IndexError:
            pass
        else:
            if node.tag != "sec":
                return
            if node.find("title") and node.find("p") is None:
                ref_list_node.insert(0, node.find("title"))
                body.remove(node)

    def fix_body_begin(self, body):
        if body.xpath("sec[@sec-type='intro']"):
            for item in body.xpath("sec"):
                if item.get("sec-type") != "intro":
                    body.remove(item)
                    continue
                break


class PreMainHTMLPipe(plumber.Pipe):

    def _process_before_references(self, raw, xml):
        text = raw.main_html_paragraphs["before references"]
        if text:
            node = ET.Element("temp")
            node.set("type", "body")
            node.text = ET.CDATA(text)
            xml.find(".").append(node)

    def _process_references(self, raw, xml):
        references = raw.main_html_paragraphs["references"]
        if not references:
            return
        back = xml.find(".//temp[@type='back']")
        if back is None:
            back = ET.Element("temp")
            back.set("type", "back")
            xml.find(".").append(back)

        ref_list_node = ET.Element("ref-list")
        back.insert(0, ref_list_node)
        for i, item in enumerate(references or []):
            # item.keys() = (text, index, reference_index, part)
            # cria o elemento `ref` com conteúdo de `item['text']`
            ref = ET.Element("ref")

            try:
                ref_index = item["reference_index"]
                ref.set("id", f"B{ref_index}")
            except KeyError:
                ref_index = item.get("guessed_reference_index")
                if ref_index:
                    ref.set("id", f"B{ref_index}")
                    ref.set("guessed_reference_index", "true")

            mixed_citation = ET.Element("temp")
            mixed_citation.set("type", "mixed-citation")
            mixed_citation.text = ET.CDATA(item["text"])
            ref.append(mixed_citation)

            # adiciona `ref` ao `ref-list`
            ref_list_node.append(ref)

    def _process_after_references(self, raw, xml):
        """
        Processa o conteúdo após as referências bibliográficas.

        Args:
            raw: Objeto contendo os parágrafos HTML estruturados
            xml: Documento XML sendo construído
        """
        text = raw.main_html_paragraphs["after references"]
        if text:
            node = ET.Element("temp")
            node.set("type", "back")
            node.text = ET.CDATA(text)
            xml.find(".").append(node)

    def transform(self, data):
        """
        Método principal que orquestra a transformação do documento.

        Args:
            data: Tupla contendo (raw, xml)

        Returns:
            data: Tupla processada (raw, xml)
        """
        raw, xml = data

        # Processa cada seção do documento
        self._process_before_references(raw, xml)
        self._process_after_references(raw, xml)
        self._process_references(raw, xml)
        return data


class PreTranslatedHTMLPipe(plumber.Pipe):
    """
    Esta etapa espera que exista o dict `raw.translated_html_by_lang`
    cujas chaves são os idiomas e os valores são os textos

    O texto completo das traduções é um dicionário composto por dois items:
    - 'before references': texto antes das referências bibliográficas
    - 'after references': texto após as referências bibliográficas

    A partir de cada translated_html_by_lang é gerado um sub-article do tipo
    translation com os elementos body e back
    """

    def transform(self, data):
        raw, xml = data

        article = xml.find(".")
        idx = 0
        for lang, texts in raw.translated_html_by_lang.items():
            idx += 1
            sub_article = ET.Element("sub-article")
            sub_article.set("id", f"s0{idx}")
            sub_article.set("article-type", "translation")
            sub_article.set("{http://www.w3.org/XML/1998/namespace}lang", lang)
            article.append(sub_article)

            # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
            # acusará erro de má formação do XML. O conteúdo do CDATA será
            # tratado em uma etapa futura

            # texts['before references'] é str
            try:
                node = ET.Element("temp")
                node.set("type", "body")
                node.text = ET.CDATA(texts["before references"])
                sub_article.append(node)

            except KeyError:
                pass

            try:
                node = ET.Element("temp")
                node.set("type", "back")
                node.text = ET.CDATA(texts["after references"])
                sub_article.append(node)
            except KeyError:
                pass
        _report(xml, func_name=type(self))
        return data


class CompleteDispFormulaPipe(plumber.Pipe):

    def wrap_graphic_in_disp_formula(self, disp_formula_id, graphic):
        try:
            parent = graphic.getparent()

            disp_formula = ET.Element("disp-formula")
            disp_formula.set("id", disp_formula_id)
            disp_formula.append(graphic)

            parent.append(disp_formula)

        except Exception as e:
            logging.error(
                f"Unable to wrap graphic in disp-formula: {ET.tostring(graphic)}"
            )
            logging.exception(e)

    def get_id(self, xml):
        return len(xml.xpath(".//disp-formula")) + 1

    def transform(self, data):
        raw, xml = data

        for item in xml.xpath(".//*[graphic]"):
            if item.tag != "p":
                continue
            if len(item.getchildren()) > 1:
                continue
            texts = "".join(item.xpath(".//text()")).strip()
            if texts:
                continue
            disp_formula_id = f"e{self.get_id(xml)}"
            self.wrap_graphic_in_disp_formula(disp_formula_id, item.find("graphic"))

        return raw, xml


class XRefAssetOtherTypesPipe(plumber.Pipe):
    """
    Processa xrefs com asset_type='pdf' ou asset_type='other' para anexos e materiais suplementares.
    Converte os xrefs em elementos supplementary-material apropriados.
    """

    def _extract_file_info(self, href):
        """Extrai informações básicas do arquivo."""
        name = os.path.basename(href)
        _, ext = os.path.splitext(name)
        return name, ext

    def _create_asset_element(self, xref, element_name, name, text):
        """Cria o elemento de asset com atributos apropriados.
        <media mimetype="application" mime-subtype="pdf" xlink:href="1234-5678-scie-58-e1043-md3.pdf"/>
        """
        new_node = ET.Element(element_name or "sec")
        new_node.set("id", name)

        label = ET.Element("label")
        label.text = text

        sub_node = ET.Element("media")
        sub_node.set("mimetype", xref.get("mimetype"))
        sub_node.set("mime-subtype", xref.get("mime-subtype"))
        sub_node.set("{http://www.w3.org/1999/xlink}href", xref.get("path"))

        new_node.append(label)
        new_node.append(sub_node)

        return new_node

    def transform(self, data):
        raw, xml = data

        processed = set()

        for xref in xml.xpath(".//xref[@asset_type and @asset_type!='image']"):
            path = xref.get("path")
            if not path:
                continue

            try:
                name, ext = self._extract_file_info(path)
                text = "".join(xref.xpath(".//text()")).strip()

                xref.set("rid", name)
                element_name = None
                if text:
                    ref_type, element_name, prefix, number = detect_from_text(text)
                    if ref_type:
                        xref.set("ref-type", ref_type)

                if path in processed:
                    # elemento "asset" já foi criado
                    continue
                parent = xref.getparent()
                if parent is None:
                    continue
                new_node = self._create_asset_element(xref, element_name, name, text)
                parent.addnext(new_node)
                processed.add(path)
            except Exception as e:
                logging.error(f"Erro ao processar asset {path}: {e}")

        _report(xml, func_name=type(self))
        return data


class MarkHTMLFileToEmbedPipe(plumber.Pipe):
    """
    Marca xrefs com ... que são arquivos HTML locais para serem embedados."""

    def _is_local_html_file(self, href: str, journal_acron_folder) -> bool:
        """
        Determina se um arquivo HTML é local baseado na presença de acrônimo entre barras.

        Args:
            href: Caminho para o arquivo HTML

        Returns:
            True se for arquivo local (contém /acrônimo/), False caso contrário
        """
        # Normaliza barras
        normalized_href = href.replace("\\", "/")

        if journal_acron_folder not in normalized_href:
            return False

        # URLs absolutas não são locais
        if normalized_href.startswith("http://") or normalized_href.startswith(
            "https://"
        ):
            return False

        # Verifica padrão /acrônimo/ no caminho
        pattern = r".*/([a-zA-Z]+)/[^/]*\.html?(?:#.*)?$"
        return bool(re.search(pattern, normalized_href))

    def get_anchor_prefix_and_name_from_href(
        self, href: str
    ) -> tuple[str, str, str, str]:
        """
        Extrai o nome da âncora do href.

        Args:
            href: Caminho para o arquivo HTML

        Returns:
            Tuple containing (new_anchor_prefix, anchor, new_name, new_href)
        """
        parts = href.split("#")
        path = parts[0]
        anchor = ""
        if len(parts) > 1:
            anchor = parts[-1]
        new_anchor_prefix, _ = os.path.splitext(os.path.basename(path))
        new_name = f"{new_anchor_prefix}{anchor}"
        new_href = f"#{new_name}"
        return new_anchor_prefix, anchor, new_name, new_href

    def transform(self, data):
        raw, xml = data

        journal_acron = raw.journal and raw.journal.acronym
        if not journal_acron:
            return data
        journal_acron_folder = f"/{journal_acron}/"

        # Processa xrefs com asset_type='html'
        done_list = set()
        for a_href in xml.xpath(".//a[@href]"):
            href = (a_href.get("href") or "").strip()
            if not self._is_local_html_file(href, journal_acron_folder):
                logging.info(f"HTML não é local: {href}")
                continue
            new_anchor_prefix, anchor, new_name, new_href = (
                self.get_anchor_prefix_and_name_from_href(href)
            )
            self.update_anchor_attributes(a_href, href, anchor, new_href)
            if new_anchor_prefix in done_list:
                logging.info(f"HTML local já processado: {href}")
                continue

            try:
                # TODO: reativar processamento do HTML embedado
                # self.embed_html(a_href, href, journal_acron_folder, raw.file_reader, done_list, new_name)
                done_list.add(new_anchor_prefix)
            except Exception as e:
                logging.error(f"Erro ao processar HTML local {href}: {e}")

        _report(xml, func_name=type(self))
        return data

    def update_anchor_attributes(self, a_href, href, anchor, new_href):
        a_href.tag = "xref"
        if anchor:
            a_href.set("path", href.split("#")[0])
            a_href.set("anchor", anchor)
        else:
            a_href.set("path", href)
        a_href.set("new-href", new_href)
        a_href.set("asset_type", "html")

    def embed_html(
        self, a_href, path, journal_acron_folder, file_reader, done_list, new_name
    ):

        # Navega e processa o HTML local recursivamente
        corrected_html = get_html_to_embed(
            path, journal_acron_folder, file_reader, done_list
        )

        if not corrected_html:
            logging.warning(f"Não foi possível processar HTML: {path}")
            return False

        corrected_html.set("name", new_name)

        # Cria elemento para o conteúdo embedado
        parent = a_href.getparent()
        if parent is None:
            return False

        # Cria wrapper com conteúdo corrigido
        parent.addnext(corrected_html)
        return True

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
from scielo_classic_website.spsxml.detector import (
    analyze_xref,
    detect_from_text,
    detect_element_type,
)
from scielo_classic_website.spsxml.detector_title_parent import identify_parent_by_title
from scielo_classic_website.htmlbody.html_merger import (
    merge_html,
)
from scielo_classic_website.spsxml.detector_config_xref import (
    ASSET_TYPE_CONFIG,
)


class XMLBodyAnBackConvertException(Exception): ...


def wrap_elements(root, xpath, stop_tag, excluding_tags=None):
    excluding_tags = excluding_tags or set()
    wrap_item = None
    for item in list(root.xpath(xpath or "*")):
        if item.tag in excluding_tags:
            continue

        if item.tag == stop_tag:
            wrap_item = item
            if item.text is None and not item.getchildren() and item.tail:
                item.text = item.tail
                item.tail = None
            continue

        if item.tag in ("title", "bold"):
            new_tag = ET.Element(stop_tag)
            item.addprevious(new_tag)
            new_tag.append(item)
            wrap_item = new_tag
            continue

        if item.xpath(f".//{stop_tag}"):
            item.tag = stop_tag
            wrap_item = item                
            continue

        if wrap_item is None:
            wrap_item = ET.Element(stop_tag)
            item.addprevious(wrap_item)

        wrap_item.append(item)


def delete_tags(root):
    if root is None:
        return
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
        xml = remove_tags(fixed_html_entities)
        return get_node_from_standardized_html(element_name, xml)


def get_node_from_standardized_html(element_name, fixed_html_entities):
    if element_name != "body":
        fixed_html_entities = f"<{element_name}>{fixed_html_entities}</{element_name}>"
    try:
        hc = HTMLContent(fixed_html_entities)
        node = hc.tree.find(f".//{element_name}")
        if node is None:
            raise ValueError(f"Unable to get node from html (node is None): {fixed_html_entities}")
        return node
    except Exception as e:
        raise ValueError(f"Unable to get node from html (exception occurred: {e}): {fixed_html_entities}")


def has_previous_text(br):
    previous = br.getprevious()
    if previous is None:
        return False
    if (previous.tail or "").strip():
        return True
    parent = br.getparent()
    if parent is None:
        return False
    if (parent.text or "").strip():
        return True


def has_next_text(br):
    if (br.tail or "").strip():
        return True
    return False


def convert_html_to_xml(document):
    """
    document está em scielo_classic_website.models.document.Document.
    """
    calls = (
        convert_html_to_xml_step_10_insert_html_in_cdata,
        convert_html_to_xml_step_20_remove_cdata,
        convert_html_to_xml_step_30_embed_html,
        convert_html_to_xml_step_40_basic_html_to_xml,
        convert_html_to_xml_step_50_break_to_p,
        convert_html_to_xml_step_60_ahref_and_aname,
        convert_html_to_xml_step_70_complete_fig_and_tablewrap,
        convert_html_to_xml_step_80_fix_sec,
        convert_html_to_xml_step_90_complete_disp_formula,
        convert_html_to_xml_step_95_fix_body,
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


def convert_html_to_xml_step_10_insert_html_in_cdata(document):
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
    ppl = plumber.Pipeline(
        SetupPipe(),
        PreMainHTMLPipe(),
        PreTranslatedHTMLPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_20_remove_cdata(document):
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
    ppl = plumber.Pipeline(
        StartPipe(),
        MainHTMLPipe(),
        TranslatedHTMLPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_30_embed_html(document):
    ppl = plumber.Pipeline(
        StartPipe(),
        MarkHTMLFileToEmbedPipe(),
        RemoveEmptyTagPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_40_basic_html_to_xml(document):
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
    ppl = plumber.Pipeline(
        StartPipe(),
        XMLNormalizeSpacePipe(),
        RemoveCommentPipe(),
        FontSymbolPipe(),
        RenameElementsPipe(),
        OlPipe(),
        UlPipe(),
        TagsHPipe(),
        XMLBodyCenterPipe(),
        CreateStyleTagFromAttributePipe(),
        StylePipe(),
        SizeAttributePipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_50_break_to_p(document):
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
    ppl = plumber.Pipeline(
        StartPipe(),
        RemoveBodyOrBackBreakPipe(),
        POpenPipe(),
        FixParagraphAbsencePipe(),
        ExcludeFontPipe(),
        BoldParagraphToParagraphBoldPipe(),
        ParagraphTitlePipe(),
        WrapElementsPipe(),
        DivPipe(),
        RemoveHTMLTagsPipe(),
        RemoveSpanTagsPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_60_ahref_and_aname(document):
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


def convert_html_to_xml_step_70_complete_fig_and_tablewrap(document):
    
    ppl = plumber.Pipeline(
        StartPipe(),
        InlineGraphicPipe(),
        InsertGraphicInFigPipe(),
        InsertGraphicInTablewrapPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_80_fix_sec(document):
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
    ppl = plumber.Pipeline(
        StartPipe(),
        XMLEmptyBoldPipe(),
        RemoveDuplicatedTagSubtagPipe(),
        XMLBoldToTitlePipe(),
        XMLIdentifyTitleParentPipe(),
        XMLSecPipe(),
        ReferenceTitlePipe(),
        # XMLStripFrontTextPipe(),
        WrapFnPipe(),
        RemoveDuplicatedTagSubtagPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_90_complete_disp_formula(document):
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
    ppl = plumber.Pipeline(
        StartPipe(),
        CompleteDispFormulaPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_95_fix_body(document):
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
    ppl = plumber.Pipeline(
        StartPipe(),
        XMLStripFrontTextPipe(),
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

    def _process_before_references(self, xml):
        node = xml.find(".//temp[@type='body']")
        if node is not None:
            body = text_to_node("body", node.text)
            xml.find(".").insert(0, body)

    def _process_after_references(self, xml):
        node = xml.find(".//temp[@type='back']")
        if node is not None:
            text = "".join(node.itertext()).strip()
            if not text:
                return
            div = text_to_node("div", node.text)
            back = ET.Element("back")
            back.append(div)
            xml.find(".").append(back)

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
        self._process_before_references(xml)
        self._process_after_references(xml)

        ref_list_node = xml.find(".//ref-list")
        if ref_list_node is not None:
            back = xml.find(".//back")
            if back is None:
                back = ET.Element("back")
                xml.find(".").append(back)
            back.insert(0, ref_list_node)

        for item in xml.xpath(".//temp[@type='mixed-citation']"):
            parent = item.getparent()
            new_node = text_to_node("mixed-citation", item.text)
            for child in new_node.xpath(".//*"):
                if child.tag in ("sup", "sub", "italic", "bold", "ext-link", "xref"):
                    continue
                child.tag = "STRIPTAG"
            ET.strip_tags(new_node, "STRIPTAG")
            parent.replace(item, new_node)
        
        remove_items = []
        for item in xml.xpath(".//ref[@id='BNone']"):
            mixed_citation = item.find(".//mixed-citation")
            text = "".join(mixed_citation.itertext()).strip()
            if not text:
                remove_items.append(item)
        for item in remove_items:
            parent = item.getparent()
            parent.remove(item)
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
                if int(s) >= 3:
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
        for item in node.getchildren():
            text = "".join(item.itertext()).strip()
            if not text:
                continue
            item.tag = "list-item"

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

        for item in node.getchildren():
            text = "".join(item.itertext()).strip()
            if not text:
                continue
            item.tag = "list-item"

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
                node.tag = "STRIPTAG"
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

    def parser_node(self, node, journal_acron, journal_acron_folder, context):
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
            if context.tag in ("ref-list", ):
                # ext-link
                return self._create_ext_link(node)
            else:
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
        for context in xml.xpath(".//body|.//ref-list"):
            for a_href_node in context.xpath(".//a[@href]"):
                self.parser_node(a_href_node, journal_acron, journal_acron_folder, context)
        for context in xml.xpath(".//back"):
            for a_href_node in context.xpath(".//a[@href]"):
                self.parser_node(a_href_node, journal_acron, journal_acron_folder, context)
        ET.strip_tags(xml, "STRIPTAG")
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
                node.tag = "STRIPTAG"
        ET.strip_tags(root, "STRIPTAG")

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
        if "corresp" in rid.lower():
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
    Procura graphic nos irmãos ascendentes de fig e table-wrap e os envolve.
    Antes:
    <fig id="f1"/>
    <p align="center">
        <graphic xlink:href="f1.jpg"/>
    </p>

    Resultado esperado:
    <fig id="f1">
        <graphic xlink:href="f1.jpg"/>
    </fig>
    <p align="center"> </p>
    """
    def transform(self, data):
        raw, xml = data
        _process(xml, "fig[@id]", self.wrap_graphic)
        return data

    def wrap_graphic(self, fig):
        item = fig
        if item.xpath(".//graphic"):
            return
        graphic = self.find_graphic(item)
        if graphic is None:
            logging.error(f"InsertGraphicInFigPipe - no graphic found for fig {ET.tostring(item)}")
            return
        fig.append(graphic)
        
    def find_graphic(self, item):
        graphic = self.find_graphic_in_siblings(item)
        if graphic is not None:
            return graphic
        graphic = self.find_graphic_in_upper_siblings(item)
        if graphic is not None:
            return graphic
    
    def find_graphic_in_siblings(self, item):
        if item is None:
            return None
        for i in range(3):
            sibling = item.getnext()
            if sibling is None:
                return
            if sibling.tag == "graphic":
                return sibling
            graphic = sibling.find(".//graphic")
            if graphic is not None:
                return graphic
            item = sibling
    
    def go_up(self, node):
        parent = node.getparent()
        if parent is None:
            return None
        if parent.tag in ("body", "back"):
            return None
        return parent
    
    def find_graphic_in_upper_siblings(self, item):
        if item is None:
            return None
        node = item
        for i in range(3):
            node = self.go_up(node)
            if node is None:
                return None
            graphic = self.find_graphic_in_siblings(node)
            if graphic is not None:
                return graphic


class InsertGraphicInTablewrapPipe(plumber.Pipe):
    """
    Procura graphic nos irmãos ascendentes de fig e table-wrap e os envolve.
    Antes:
    <fig id="f1"/>
    <p align="center">
        <graphic xlink:href="f1.jpg"/>
    </p>

    Resultado esperado:
    <fig id="f1">
        <graphic xlink:href="f1.jpg"/>
    </fig>
    <p align="center"> </p>
    """
    def transform(self, data):
        raw, xml = data
        _process(xml, "table-wrap[@id]", self.wrap_graphic)
        return data

    def wrap_graphic(self, tablewrap):
        item = tablewrap
        if item.xpath(".//graphic|.//table"):
            return
        graphic = self.find_graphic(item)
        if graphic is None:
            return
        tablewrap.append(graphic)
        logging.info(f"InsertGraphicInTablewrapPipe - feito {ET.tostring(tablewrap)}")
        
    def find_graphic(self, item):
        graphic = self.find_graphic_in_siblings(item)
        if graphic is not None:
            return graphic
        graphic = self.find_graphic_in_upper_siblings(item)
        if graphic is not None:
            return graphic
    
    def find_graphic_in_siblings(self, item):
        if item is None:
            return None
        while True:
            sibling = item.getnext()
            if sibling is None:
                return
            if sibling.tag in ("graphic", "table"):
                return sibling
            graphic = sibling.find(".//graphic|.//table")
            if graphic is not None:
                return graphic
            item = sibling
    
    def go_up(self, node):
        parent = node.getparent()
        if parent is None:
            return None
        if parent.tag in ("body", "back"):
            return None
        return parent
    
    def find_graphic_in_upper_siblings(self, item):
        if item is None:
            return None
        node = item
        while True:
            node = self.go_up(node)
            if node is None:
                return None
            graphic = self.find_graphic_in_siblings(node)
            if graphic is not None:
                return graphic


class RemoveEmptyTagPipe(plumber.Pipe):
    """
    Remove parágrafo vazio, ou que contenha somente espaços em branco.

    Ex: <p> </p>
    """
    def mark_span_spelle_to_strip(self, xml):
        for item in list(xml.xpath(".//span[@class='SpellE']")):
            item.tag = "TOSTRIP"
        ET.strip_tags(xml, "TOSTRIP")
            
    def mark_tag_to_strip(self, node):
        if node.tag not in ("div", "p", "span", "bold", "italic", "sup", "sub"):
            return None
        # Verifica se node.text tem conteúdo.
        if "".join(node.itertext()).strip():
            return None
        # Verifica se existe algum filho no node.
        if node.getchildren():
            return None
        node.tag = "TOSTRIP"

    def remove_empty_tags(self, xml):
        while True:
            for item in list(xml.xpath(".//*[not(*)]")):
                self.mark_tag_to_strip(item)
            if not xml.xpath(".//TOSTRIP"):
                break
            ET.strip_tags(xml, "TOSTRIP")

    def transform(self, data):
        raw, xml = data
        self.mark_span_spelle_to_strip(xml)
        self.remove_empty_tags(xml)
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

    def parser_node(self, node):
        for graphic in node.xpath("graphic"):
            if self.is_graphic_inline(graphic):
                graphic.tag = "inline-graphic"

    def transform(self, data):
        raw, xml = data
        for parent in xml.xpath(".//*[graphic]"):
            self.parser_node(parent)
        return data

    def is_graphic_inline(self, graphic):
        previous = graphic.getprevious()
        if previous is not None:
            previous_tail = (previous.tail or "").strip()
            if previous_tail:
                return True
            
        text = graphic.getparent().text
        if text and text.strip():
            return True
        
        tail = graphic.tail
        if tail and tail.strip():
            return True
        return False


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
            except KeyError:
                ref_index = item.get("guessed_reference_index")
                ref.set("guessed_reference_index", "true")

            ref.set("id", f"B{ref_index}")            
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
        logging.info(f"Creating asset element for xref with path: xref={xref}, element_name={element_name}, name={name}, text={text}")
    
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

        for xref in xml.xpath(".//xref[@asset_type and @asset_type!='image' and @asset_type!='html']"):
            events = []
            path = xref.get("path")
            if not path:
                continue

            try:
                
                events.append(f"Processing asset xref: {path}")

                name, ext = self._extract_file_info(path)
                events.append(f"Asset name: {name}, extension: {ext}")
                text = "".join(xref.xpath(".//text()")).strip()
                events.append(f"Asset text: {text}")

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
                events.append(f"Creating asset element: {element_name} with id: {name}")
                new_node = self._create_asset_element(xref, element_name, name, text)
                events.append(f"Inserting asset element after parent.")
                parent.addnext(new_node)
                events.append(f"Asset element created successfully.")
                processed.add(path)
            except Exception as e:
                logging.error(f"Erro ao processar asset {path}: {e}")
                logging.info(events)

        _report(xml, func_name=type(self))
        return data


class MarkHTMLFileToEmbedPipe(plumber.Pipe):
    """
    Marca xrefs com ... que são arquivos HTML locais para serem embedados."""

    def html_reader(self, path, encoding, journal_acron_folder):
        return path

    def transform(self, data):
        raw, xml = data

        try:
            html_reader = raw.html_reader
        except AttributeError:
            # TODO implementar html_reader em raw
            html_reader = self.html_reader

        journal_acron = raw.journal and raw.journal.acronym
        if not journal_acron:
            return data
        journal_acron_folder = f"/{journal_acron}/"

        for body in xml.xpath(".//body"):
            body_str = ET.tostring(body, encoding="iso-8859-1").decode("iso-8859-1")
            input_html = f"<html>{body_str}</html>"
            new_body = merge_html(
                input_html,
                journal_acron_folder=journal_acron_folder,
                encoding="iso-8859-1",
                content_reader=html_reader
            )
            parent = body.getparent()
            parent.replace(body, new_body)
        
        for back in xml.xpath(".//back"):
            back.tag = "body"
            back_str = ET.tostring(back, encoding="iso-8859-1").decode("iso-8859-1")
            input_html = f"<html>{back_str}</html>"
            new_back = merge_html(
                input_html,
                journal_acron_folder=journal_acron_folder,
                encoding="iso-8859-1",
                content_reader=html_reader
            )
            new_back.tag = "back"
            parent = back.getparent()
            parent.replace(back, new_back)
        return data


class XMLBodyCenterPipe(plumber.Pipe):
    """
    Converte elementos <center> para <title>.
    
    O elemento <center> não é apropriado para documentos XML científicos,
    sendo convertido para <title> que é mais semântico para enfatizar texto.
    """
    
    def transform(self, data):
        raw, xml = data
        for item in xml.xpath(".//body|.//back"):
            self.rename_center(item)
        return data

    def rename_center(self, root):
        # Converte todos os elementos center para title
        for center in root.xpath("center| *[@align='center']"):
            previous = center.getprevious()
            if previous is not None:
                if previous.tag == "a":
                    center.insert(0, previous)
            if center.xpath(".//img|.//a[@href]"):
                center.tag = "p"
                continue
            text = "".join(center.xpath(".//text()")).strip()
            children = list(center.getchildren())
            if not children and not text:
                center.tag = "STRIPTAG"
                continue
            if children:
                center.tag = "p"
                continue
            center.tag = "title"


class XMLBoldToTitlePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        self.join_bold_and_bold(xml)
        self.replace_bold_by_title(xml)
        self.strip_bold_from_bold_title(xml)
        self.strip_bold_from_title_bold(xml)
        for title in xml.xpath(".//title[break]"):
            for item in title.xpath("break"):
                item.tag = "TAGTOSTRIP"
        ET.strip_tags(xml, "TAGTOSTRIP")
        return data

    def join_bold_and_bold(self, xml):
        for node in xml.xpath(".//bold[following-sibling::node()[1][self::bold]]"):
            bold = node.getnext()
            if bold.text:
                node.tail = (node.tail or "") + bold.text
            bold.text = ""
            for child in bold.getchildren():
                node.append(child)
            bold.tag = "TAGTOSTRIP"
        ET.strip_tags(xml, "TAGTOSTRIP")
            
    def strip_bold_from_bold_title(self, xml):
        for node in xml.xpath(".//bold[title]"):
            node.tag = "TAGTOSTRIP"
        ET.strip_tags(xml, "TAGTOSTRIP")

    def strip_bold_from_title_bold(self, xml):
        for node in xml.xpath(".//title[bold]"):
            if len(node.getchildren()) == 0:
                continue
            child = node.getchildren()[0]
            if (child.tail or "").strip():
                continue
            child.tag = "TAGTOSTRIP"
        ET.strip_tags(xml, "TAGTOSTRIP")

    def replace_bold_by_title(self, xml):
        for node in xml.xpath(f".//p[bold]"):
            for first in node.getchildren():
                if first.tag == "bold":
                    first.tag = "title"
                break

        for node in xml.xpath(f".//*[bold]"):
            node_text = "".join(node.xpath(".//text()")).strip()
            bold_node = node.find(".//bold")
            bold_text = "".join(bold_node.xpath(".//text()")).strip()
            if node_text == bold_text:
                bold_node.tag = "title"


class XMLEmptyBoldPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for node in xml.xpath(".//bold"):
            text = "".join(node.xpath(".//text()")).strip()
            if not text:
                node.tag = "TAGTOSTRIP"
        ET.strip_tags(xml, "TAGTOSTRIP")
        return data


class XMLIdentifyTitleParentPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for parent_title in xml.xpath(".//*[title]"):
            self.identify_title_parent(parent_title)
        ET.strip_tags(xml, "TAGTOSTRIP")
        return data
    
    def identify_title_parent(self, parent_title):
        title = parent_title.find("title")
        text = "".join(title.itertext()).strip()
        if not text:
            title.tag = "TAGTOSTRIP"
            return
        data = detect_element_type(text)
        tag = data.get("element_type")
        if not tag:
            tag = identify_parent_by_title(text)

        attrvalue = data.get("type_attribute")
        self.set_tag_and_attr(parent_title, tag, attrvalue)

    def set_tag_and_attr(self, parent_title, tag, attrvalue):
        if not tag:
            return None
        if tag == "ref-list":
            parent_title.set("ref-list-title", "true")
            parent_title.find('title').set("ref-list-title", "true")
        else:
            parent_title.tag = tag
        if attrvalue:
            parent_title.set(f"{tag}-type", attrvalue)


class XMLSecPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for node in xml.xpath(".//body|.//back"):
            self.add_sec(node)
            self.wrap_subsec(node)
        return data

    def add_sec(self, root):
        if root.find("sec") is None:
            return
        sec_node = None
        children = list(root.getchildren())
        if not [child.tag for child in children if child.tag not in ("sec", "ref-list")]:
            return
        for root_child in children:
            if root_child.tag == "ref-list":
                continue
            if root_child.tag == "sec":
                sec_node = root_child
                continue
            if sec_node is None:
                sec_node = ET.Element("sec")
                root_child.addprevious(sec_node)
            sec_node.append(root_child)

    def wrap_subsec(self, root):
        if root.find("sec") is None:
            return
        sec_nodes = list(root.getchildren())
        for sec_node in sec_nodes:
            # todos são sec
            self.wrap_items(sec_node)

    def wrap_items(self, sec_node):
        for child in list(sec_node.xpath("p[title]")):
            child.tag = "sec"
        if sec_node.find("sec") is None:
            return
        wrap = None
        for child in list(sec_node.getchildren()):
            if child.tag == "sec":
                wrap = child
                continue
            if wrap is None:
                wrap = ET.Element("sec")
                child.addprevious(wrap)
            wrap.append(child)


class XMLStripFrontTextPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            deleted = self.strip_front_text_by_sec_intro(body)
            if not deleted:
                self.strip_front_text_by_other_element_name_children(body, "kwd-group|abstract")
            if not deleted:
                deleted = self.strip_front_text_by_other_element_name_sublevel(body, "kwd-group")
            if not deleted:
                deleted = self.strip_front_text_by_other_element_name_sublevel(body, "abstract")
        return data
    
    def strip_front_text_by_sec_intro(self, body):
        intro = body.xpath("sec[@sec-type='intro']")
        if not intro:
            return False
        intro = intro[0]
        todelete = []
        for item in list(body.getchildren()):
            if item is intro:
                break
            else:
                todelete.append(item)
        for item in todelete:
            body.remove(item)
        return bool(todelete)

    def strip_front_text_by_other_element_name_children(self, body, element_name):
        elements = body.xpath(f"{element_name}")
        if not elements:
            return False
        todelete = []
        for child in list(body.getchildren()):
            todelete.append(child)
            if child is elements[-1]:
                break
        for item in todelete:
            body.remove(item)
        return bool(todelete)

    def strip_front_text_by_other_element_name_sublevel(self, body, element_name):
        deleted = []
        while True:
            xpath = f".//{element_name}"
            elements = body.xpath(xpath)
            if not elements:
                return False
            todelete = []
            for child in list(body.getchildren()):
                # marca todos os nós até encontrar aquele que contém .//element_name
                elements = child.xpath(xpath)
                if not elements:
                    todelete.append(child)
                    continue
                for elem in elements:
                    parent = elem.getparent()
                    for sibling in list(parent.getchildren()):
                        # marca todos os nós irmãos até encontrar o ele mesmo
                        todelete.append(sibling)
                        if sibling is elem:
                            break
                break
            for item in todelete:
                parent = item.getparent()
                if parent is not None:
                    parent.remove(item)
            deleted.append(bool(todelete))
        return any(deleted)


class ReferenceTitlePipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            self.complete_ref_list_title(body)
            break
        return data

    def complete_ref_list_title(self, body):
        try:
            node = body.xpath(".//*[@ref-list-title='true']")[0]
        except IndexError:
            return

        back = body.getnext()
        if back is None or back.tag != "back":
            return

        ref_list_node = back.find(".//ref-list")
        if ref_list_node is None:
            return
        if ref_list_node.find("title") is not None:
            return
        ref_list_node.insert(0, node.find("title"))


class WrapFnPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for root in xml.xpath(".//body|.//back"):
            self.wrap_fn(root)
        
            for parent in root.xpath("*[fn]"):
                fns = parent.xpath("fn")
                if len(fns) > 1:
                    if parent.tag in ("p", "sec", "div"):
                        parent.tag = "fn-group"
                    else:
                        fngroup = ET.Element("fn-group")
                        fns[0].addprevious(fngroup)
                        for fn in fns:
                            fngroup.append(fn)
        return data

    def wrap_fn(self, xml):
        for node in xml.xpath(".//fn"):
            if node.xpath("*"):
                continue
            for sibling in list(node.itersiblings()):
                if sibling.tag == "fn":
                    break
                if sibling.get("id"):
                    break
                node.append(sibling)


class RemoveDuplicatedTagSubtagPipe(plumber.Pipe):
    """
    Remove sec e p duplicados.
    """ 

    def transform(self, data):
        raw, xml = data
        for root in xml.xpath(".//body|.//back"):
            self.remove_duplicated_tag(root, "title")
            self.remove_duplicated_tag(root, "p")
            self.remove_duplicated_tag(root, "sec")
        return data

    def remove_duplicated_tag(self, root, tag_name):
        while True:
            xpath = f".//{tag_name}[{tag_name}]"
            for node in list(root.xpath(xpath)):
                text = (node.text or "").strip()
                if text:
                    continue
                children = list(node.getchildren())
                child = children[-1]
                if has_next_text(child):
                    continue
                tags = set([child.tag for child in children])
                if len(tags) > 1:
                    # há tags diferentes entre os filhos
                    continue
                node.tag = "TAGTOSTRIP"
            if not root.xpath("//TAGTOSTRIP"):
                break
            ET.strip_tags(root, "TAGTOSTRIP")


class FixParagraphAbsencePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            if not body.xpath(".//p|.//div"):
                self.fix_p_absence(body)
        for back in xml.xpath(".//back"):
            if not back.xpath(".//p|.//div"):
                self.fix_p_absence(back)
        return data

    def fix_p_absence(self, root):
        self.create_p(root)
        self.mark_double_breaks(root)
        self.replace_span_followed_by_break_by_p(root)
        self.replace_span_which_only_child_is_doublebreak_with_p(root)
        self.replace_font_followed_by_break_by_p_or_sec(root)
        self.exclude_unecessary_breaks(root)
    
    def create_p(self, root):
        if not root.xpath("break"):
            return
        p = None
        for item in list(root.getchildren()):
            if item.tag == "break":
                p = item
                p.tag = "p"
            else:
                if p is None:
                    p = ET.Element("p")
                p.append(item)

    def exclude_unecessary_breaks(self, root):
        for br in list(root.xpath(".//break")):
            previous_text = has_previous_text(br)
            if previous_text:
                continue
            if has_next_text(br):
                continue
            if br.getnext() is not None:
                continue
            br.tag = "TOREMOVE"
        ET.strip_tags(root, "TOREMOVE")

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
            "//*[following-sibling::node()[1][self::DOUBLEBREAK]]"
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


class BoldParagraphToParagraphBoldPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        self.exchange_bold_p(xml)
        return data

    def exchange_bold_p(self, xml):
        for node in xml.xpath(".//bold[p]"):
            if len(node.getchildren()) == 1:
                p = node.find("p")
                p.tag = "bold"
                node.tag = "p"


class ExcludeFontPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        self.strip_font_which_has_only_text(xml)
        self.strip_font_font(xml)
        self.strip_p_font(xml)
        return data

    def strip_font_which_has_only_text(self, xml):
        while True:
            nodes = list(xml.xpath(".//font[not(*)]"))
            if not nodes:
                break
            for node in nodes:
                node.tag = "STRIPTAG"
            ET.strip_tags(xml, "STRIPTAG")

    def strip_font_font(self, xml):
        for node in xml.xpath(".//font[font]"):
            previous = node.getprevious()
            if len(node.getchildren()) == 1:
                font = node.find("font")
                font.tag = "STRIPTAG"
            if previous is not None and previous.tag == "a":
                node.insert(0, previous)
        ET.strip_tags(xml, "STRIPTAG")

    def strip_p_font(self, xml):
        for node in xml.xpath(".//p[font]"):
            if len(node.getchildren()) == 1:
                font = node.find("font")
                font.tag = "STRIPTAG"
        ET.strip_tags(xml, "STRIPTAG")


class ParagraphTitlePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for node in xml.xpath(".//body|.//back"):
            self.exclude_p_title_children(node)
        return data

    def exclude_p_title_children(self, node):
        for p_title in node.xpath(".//p[title]|.//p[bold]"):
            parent = p_title.getparent()
            if len(p_title.xpath(".//title|.//bold")) != 1:
                p_title_title = p_title.find("title")
                if p_title_title is not None:
                    p_title_title.tag = "bold"
                continue
            try:
                first = p_title.getchildren()[0]
            except IndexError:
                continue
            if first.tag == "bold":
                first.tag = "title"
            if first.tag != "title":
                continue
            for child in list(first.xpath(".//*")):
                if child.tag in ("bold", "italic", "sup", "sub", "xref"):
                    continue
                child.set("tag", child.tag)
                child.tag = "STRIPTAG"
        ET.strip_tags(node, "STRIPTAG")


class POpenPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        
        for root in xml.xpath(".//body|.//back"):
            self.wrap(root)
        return data

    def wrap(self, root):
        if not root.xpath("p[@type='open']"):
            return
        # wrap elements
        wrap_elements(
            root,
            "p",
            "p",
        )


class WrapElementsPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for root in xml.xpath(".//div"):
            self.wrap_elements(root)
        for root in xml.xpath(".//body"):
            self.wrap_elements(root)
        for root in xml.xpath(".//back"):
            self.wrap_elements(root)
        return data

    def clean(self, root, tag):
        for item in list(root.xpath(f".//{tag}")):
            if item.getchildren():
                continue
            text = "".join(item.itertext()).strip()
            if not text:
                item.tag = "STRIPTAG"
        ET.strip_tags(root, "STRIPTAG")
        
    def wrap_elements(self, root):
        self.clean(root, "bold")
        self.clean(root, "span")
        self.clean(root, "font")
        
        div = root.xpath("div")
        if div:
            wrap_elements(root, xpath=None, stop_tag="div", excluding_tags={"ref-list"})
            return
        
        p = root.xpath("p")
        if p:
            wrap_elements(root, xpath=None, stop_tag="p", excluding_tags={"ref-list"})
            return


class DivPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for node in list(xml.xpath(".//div[break]")):
            if node.find("p") is None and node.find("div") is None:
                node.tag = "p"
        for node in list(xml.xpath(".//div[div]")):
            if node.find("p") is None:
                node.tag = "sec"
                for child in node.xpath("div"):
                    child.tag = "p"
        for node in list(xml.xpath(".//div[p]")):
            node.tag = "sec"
        return data


class RemoveBodyOrBackBreakPipe(plumber.Pipe):
    """
    Remove parágrafo vazio, ou que contenha somente espaços em branco.

    Ex: <p> </p>
    """

    def transform(self, data):
        raw, xml = data
        for parent in xml.xpath(".//body[break]|.//back[break]"):
            if not parent.xpath("p | div"):
                continue
            for item in parent.xpath("break"):
                previous_text = has_previous_text(item)
                next_text = has_next_text(item)
                if previous_text or next_text:
                    continue
                item.tag = "REMOVE_EXCEDING_BREAK_TAG"
        ET.strip_tags(xml, "REMOVE_EXCEDING_BREAK_TAG")
        return data
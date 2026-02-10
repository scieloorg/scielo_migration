import traceback
import sys
import logging
import os
from copy import deepcopy
import re

import plumber
from lxml import etree as ET

from scielo_classic_website.htmlbody.html_body import html_to_node
from scielo_classic_website.spsxml.detector import (
    analyze_xref,
    detect_from_text,
    detect_element_type,
    detect_sec_type,
    detect_from_id,
)
from scielo_classic_website.spsxml.detector_title_parent import identify_parent_by_title
from scielo_classic_website.htmlbody.html_merger import (
    merge_html,
)
from scielo_classic_website.spsxml.detector_config_xref import (
    ASSET_TYPE_CONFIG,
)


class XMLBodyAnBackConvertException(Exception): ...


def is_last_item_in_parent(node):
    if node.tail and node.tail.strip():
        return False
    next_sibling = node.getnext()
    if next_sibling is not None:
        return False
    return True


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
        # convert_html_to_xml_step_90_complete_disp_formula,
        convert_html_to_xml_step_95_fix_body,
    )
    document.exceptions = []
    document.xml_body_and_back = []
    for i, call_ in enumerate(calls, start=1):
        try:
            document.xml_body_and_back.append(call_(document))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.info(f"Convert HTML to XML - step {i} failed {call_.__name__}")
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
    """
    Incorpora conteúdo HTML de arquivos referenciados recursivamente na estrutura XML.

    Esta função processa um documento através de um pipeline que identifica e marca
    arquivos HTML mencionados no HTML principal para serem incorporados recursivamente
    dentro da estrutura XML, permitindo a inclusão de conteúdo de múltiplos arquivos
    HTML de forma aninhada.

    Parameters
    ----------
    document : Document
        Objeto documento a ser processado para conversão de HTML para XML
        com incorporação recursiva de arquivos HTML referenciados.

    Returns
    -------
    Document
        Documento transformado com arquivos HTML incorporados recursivamente
        na estrutura XML.

    Raises
    ------
    StopIteration
        Se o pipeline não produz saída.
    """
    ppl = plumber.Pipeline(
        StartPipe(),
        MarkHTMLFileToEmbedPipe(),
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
        SizeAttributePipe(),
        StripTagsPipe(),
        XMLEmptyTagsPipe(),
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
        ExcludeMultipleBreaksPipe(),
        FixParagraphAbsencePipe(),
        RemoveHTMLTagsPipe(),
        POpenPipe(),
        WrapElementsPipe(),
        DivPipe(),
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
        XMLEmptyTagsPipe(),
        XMLBoldToTitlePipe(),
        RemoveDuplicatedTagSubtagPipe(),
        XMLIdentifyTitleParentPipe(),
        XMLWrapTitleTailPipe(),
        XMLFixBodySecHierarchyPipe(),
        XMLSecPipe(),
        ReferenceTitlePipe(),
        # XMLStripFrontTextPipe(),
        WrapFnPipe(),
        RemoveDuplicatedTagSubtagPipe(),
        AckPipe(),
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
            body = html_to_node("body", node.text)
            xml.find(".").insert(0, body)

    def _process_after_references(self, xml):
        node = xml.find(".//temp[@type='back']")
        if node is not None:
            text = "".join(node.itertext()).strip()
            if not text:
                return
            div = html_to_node("div", node.text)
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
            new_node = html_to_node("mixed-citation", item.text)
            for child in new_node.xpath(".//*"):
                if child.tag in ("sup", "sub", "italic", "bold", "ext-link", "xref"):
                    continue
                child.tag = "STRIPTAG"
            ET.strip_tags(new_node, "STRIPTAG")
            parent.replace(item, new_node)
        
        remove_items = []
        for item in xml.xpath(".//ref"):
            mixed_citation = item.find(".//mixed-citation")
            if mixed_citation is None:
                remove_items.append(item)
                continue
            text = "".join(mixed_citation.itertext()).strip()
            if not text:
                remove_items.append(item)
                continue
            ref_id = item.get("id")
            if not ref_id or "None" in ref_id:
                remove_items.append(item)
                continue
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
                    body = html_to_node("body", temp_body.text)
                    sub_article.append(body)
                except KeyError:
                    pass
            temp_back = sub_article.find(".//temp[@type='back']")
            if temp_back is not None:
                try:
                    back = html_to_node("back", temp_back.text)
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
    TAGS = ["font", "small", "big", "s", "lixo", "center", "span"]

    def transform(self, data):
        raw, xml = data
        ET.strip_tags(xml, self.TAGS)
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
        self.fix_style_tags(xml)
        return data
    
    def fix_style_tags(self, xml):
        for node in xml.xpath(".//*[@style]"):
            self.fix_style_tag(node, self.match_style(node))
        ET.strip_tags(xml, "striptag")
    
    def fix_style_tag(self, node, style):
        style = self.match_style(node)
        if not style:
            return
        text = "".join(node.itertext()).strip()
        if not text:
            node.tag = "striptag"
            return
        if node.tag == "p":
            new_p = ET.Element("p")
            node.addprevious(new_p)
            new_p.append(node)
            node.tag = style
            return
        children = node.getchildren()
        error = False
        for child in children:
            if child.tag not in ("bold", "sup", "sub", "italic", "underline", "p"):
                error = True
                break
        if not error:
            node.tag = style

    def match_style(self, node):
        for style in ("bold", "sup", "sub", "italic", "underline"):
            if style in node.get("style"):
                return style


class SizeAttributePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        self.handle_font_size(xml)
        return data

    def handle_font_size(self, xml):
        max_size = self.find_max_size(xml)
        logging.info(f"Max font size found: {max_size}")

        fonts = list(xml.xpath(".//font[@size]"))
        logging.info(f"Total font size found - before marking irrelevant: {len(fonts)}")
        for node in fonts:
            self.mark_irrelevant_font_size(node, max_size)
        ET.strip_tags(xml, "striptag")

        fonts = list(xml.xpath(".//font[@size]"))
        logging.info(f"Total font size found - after marking irrelevant: {len(fonts)}")
        for node in fonts:
            self.change_size_to_title(node)
        ET.strip_tags(xml, "striptag")

    def find_max_size(self, xml):
        max_size = 0
        for node in list(xml.xpath(".//font[@size]")):
            size = node.get("size")
            if size[0] == "-":
                node.attrib.pop("size")
                continue
            s = size
            if s[0] == "+":
                s = s[1:]
                node.set("size", s)
            try:
                number = int(s)
            except (ValueError, TypeError):
                number = 0
                node.attrib.pop("size")
            if number > max_size:
                max_size = number
        return max_size

    def mark_irrelevant_font_size(self, node, max_size):
        text = "".join(node.xpath(".//text()")).strip()
        if not text:
            # nao tem conteudo relevante
            node.tag = "striptag"
            return

        children = node.getchildren()
        if not children:
            # nao tem conteudo relevante
            node.tag = "striptag"
            return

        size = node.get("size")
        if int(size) < max_size:
            node.tag = "striptag"
            return

    def change_size_to_title(self, node):
        parent = node.getparent()
        if (parent.text or "").strip():
            return
        first_child = parent.getchildren()[0]
        if first_child is not node:
            return
        if first_child.tail and first_child.tail.strip():
            return
        bold = node.xpath(".//bold")
        if not bold:
            node.tag = "title"


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
            name = node.attrib.pop("name")
            ref_type, elem = detect_from_id(name)
            node.tag = elem or "element"
            node.set("id", name)
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
        parents = xml.xpath(".//*[@xref-parent='true']")
        for xref_parent in parents:
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

            if not element_name:
                logging.error(
                    f"XRefAssetTypeImagePipe - no element_name found for label: {label}"
                )
                continue

            # verifica se já existe o elemento referenciado por xref
            # cria se não existir e completa os atributos
            path = child.get("path")
            rid = child.get("rid")
            xpath = f"//*[@id='{rid}' or @name='{rid}']"

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


class StripTagsPipe(plumber.Pipe):
    """
    Remove parágrafo vazio, ou que contenha somente espaços em branco.

    Ex: <p> </p>
    """
    def mark_span_spelle_to_strip(self, xml):
        for item in list(xml.xpath(".//span[@class='SpellE']")):
            item.tag = "TOSTRIP"
        ET.strip_tags(xml, "TOSTRIP")

    def transform(self, data):
        raw, xml = data
        self.mark_span_spelle_to_strip(xml)
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
                if not is_last_item_in_parent(item):
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

        ref_list_node = ET.Element("ref-list")
        xml.find(".").append(ref_list_node)
        for i, item in enumerate(references or []):
            # item.keys() = (text, index, reference_index, part)
            # cria o elemento `ref` com conteúdo de `item['text']`
            ref = ET.Element("ref")

            try:
                ref_index = item["reference_index"]
            except KeyError:
                ref_index = item.get("guessed_reference_index")
                ref.set("guessed_reference_index", "true")
            if not ref_index:
                ref_index = str(i + 1)
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
        self.merge(journal_acron_folder, html_reader, xml)
        return data

    def merge(self, journal_acron_folder, html_reader, xml):
        try:
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
        except Exception as e:
            logging.error(f"MarkHTMLFileToEmbedPipe - error processing html embedding: {e}")
            logging.exception(e)


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
        ET.strip_tags(root, "STRIPTAG")


class XMLBoldToTitlePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        self.fix_bold_p(xml)
        self.join_bold_and_bold(xml)
        self.replace_bold_by_title(xml)
        self.strip_bold_from_bold_title(xml)
        self.strip_bold_from_title_bold(xml)
        for title in xml.xpath(".//title[break]"):
            for item in title.xpath("break"):
                item.tag = "TAGTOSTRIP"
        ET.strip_tags(xml, "TAGTOSTRIP")
        return data
    
    def fix_bold_p(self, xml):
        for node in xml.xpath(".//bold[p]"):
            children = list(node.getchildren())
            if len(children) == 1:
                node.tag = "p"
                children[0].tag = "bold"
            
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
        for node in list(xml.xpath(f".//*[bold]")):
            first_child = node.getchildren()[0]
            if first_child.tag != "bold":
                continue
            if first_child.tail and first_child.tail.strip():
                continue
            first_child.tag = "title"
        ET.strip_tags(xml, "TAGTOSTRIP")


class XMLEmptyTagsPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        self.remove_empty_tags(xml)
        return data
    
    def remove_empty_tags(self, root):
        finished = False
        while not finished:
            self.identify_empty_tags(root)
            if not root.xpath(".//TAGTOSTRIP"):
                finished = True
            ET.strip_tags(root, "TAGTOSTRIP")

    def identify_empty_tags(self, root):
        for tag in ("div", "p", "span",  "font", "italic", "bold", "sup", "sub", "b", "i"):
            for node in root.xpath(f".//{tag}"):
                if node.getchildren():
                    continue
                text = "".join(node.xpath(".//text()")).strip()
                if not text:
                    node.tag = "TAGTOSTRIP"


class XMLIdentifyTitleParentPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for root in xml.xpath(".//body|.//back"):
            for parent_title in root.xpath(".//*[title]"):
                self.identify_title_parent(parent_title)
            ET.strip_tags(root, "TAGTOSTRIP")
        return data
    
    def identify_title_parent(self, parent_title):
        text = (parent_title.text or "").strip()
        if text:
            return
        title = parent_title.find("title")
        first_child = parent_title.getchildren()[0]
        if first_child is not title:
            return
        text = (title.text or "").strip()
        if not text:
            title.tag = "TAGTOSTRIP"
            return
        tag, attrvalue = self.identify_element_and_attr_by_title(text)
        if not tag:
            parent_title.set("parent-title-unknown", "true")
            return
        self.set_tag_and_attr(parent_title, tag, attrvalue)

    def identify_element_and_attr_by_title(self, text):
        data = detect_element_type(text)
        tag = data.get("element_type")
        if tag:
            return tag, data.get("type_attribute")

        sec_type = detect_sec_type(text)
        if sec_type:
            return "sec", sec_type

        tag = identify_parent_by_title(text)
        if tag:
            return tag, None

        ref_type_text, element_name_text, prefix, number = detect_from_text(text)
        if element_name_text:
            return element_name_text, None
        return None, None

    def set_tag_and_attr(self, parent_title, tag, attrvalue):
        if not tag:
            return None
        if tag == "ref-list":
            text = "".join(parent_title.find('title').itertext()).strip()
            if len(text.split()) <= 3:
                parent_title.set("ref-list-title", "true")
                parent_title.find('title').set("ref-list-title", "true")
        else:
            parent_title.tag = tag
        if attrvalue:
            # sec-type or fn-type
            parent_title.set(f"{tag}-type", attrvalue)


class XMLSecPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for node in xml.xpath(".//body|.//back"):
            if not node.xpath(".//sec"):
                continue
            self.wrap_secs(node)
            self.wrap_subsections(node)
        return data

    def fix_parent_title_unknown(self, node):
        parent = node.getparent()
        if parent is None:
            logging.info("No parent found for node with text: %s", node.text)
            return
        if parent.get("sec-type"):
            node.tag = "sec"
            return

    def wrap_subsections(self, root):
        for node in root.xpath(".//*[@parent-title-unknown='true']"):
            self.fix_parent_title_unknown(node)

        for subsec in list(root.xpath(".//sec[not(@sec-type)]")):
            self.wrap_subsection_children(subsec)

    def wrap_subsection_children(self, sec):
        following = sec.getnext()
        while True:
            if following is None:
                break
            if following.tag == "sec":
                break
            sec.append(following)
            following = sec.getnext()
    
    def wrap_secs(self, root):
        for child in list(root.xpath(".//sec[@sec-type]")):
            self.wrap_sec_children(child)

    def wrap_sec_children(self, sec):
        following = sec.getnext()
        while True:
            if following is None:
                break
            if following.tag == "sec" and following.get("sec-type"):
                break
            sec.append(following)
            following = sec.getnext()


class XMLFixBodySecHierarchyPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            self.fix_sec_hierarchy(body)
        return data
    
    def fix_sec_hierarchy(self, body):
        for node in list(body.xpath(".//sec")):
            sec = node.xpath(".//sec[@sec-type]")
            if not sec:
                continue
            node.tag = "tostrip"
        ET.strip_tags(body, "tostrip")


class XMLStripFrontTextPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for body in xml.xpath(".//body"):
            self.save_elements(body)
            self.identify_body_beginning(body)
        return data
    
    def identify_body_beginning(self, body):
        self.strip_front_text_by_sec_intro(body)

    def save_elements(self, body):
        corresp = body.find(".//corresp")
        if corresp is not None:
            back = body.getnext()
            if back is None or back.tag != "back":
                back = ET.Element("back")
                body.addnext(back)
            back.append(corresp)
        email = body.find(".//email")
        if email is not None:
            back = body.getnext()
            if back is None or back.tag != "back":
                back = ET.Element("back")
                body.addnext(back)
            back.append(email)

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
        
        if node.find("title") is None:
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

        for root in xml.xpath(".//body|.//back"):
            p_nodes = root.xpath(".//p")
            br_nodes = root.xpath(".//br|.//break")
            font_nodes = root.xpath(".//font")
            if font_nodes and len(br_nodes) >= len(p_nodes):
                self.fix_p_absence(root)
        return data
    
    def remove_invalid_p_tags(self, root):
        for p in list(root.xpath(".//p")):
            text = "".join(p.xpath(".//text()")).strip()
            if text:
                continue
            strip = True
            for child in p.xpath(".//*"):
                if child.tag in ("img", "a"):
                    continue
                child.tag = "TAGTOSTRIP"
        ET.strip_tags(root, "TAGTOSTRIP")

    def fix_p_absence(self, root):
        self.corresp(root)
        self.fix_div(root)
        self.change_font_to_p(root)
        self.change_font_break_to_p(root)
        self.change_font_with_inner_break_to_p(root)
        self.strip_break_which_is_p_sibling(root)
        self.wrap_title_which_is_p_sibling(root)
        self.strip_p_p(root)

    def corresp(self, root):
        for aname in root.xpath(".//a[@name]"):
            if "corresp" not in aname.get("name", "").lower():
                continue
            aname.tag = "corresp"
            aname.text = aname.tail
            aname.tail = None
            for sibling in list(aname.itersiblings()):
                if sibling.tag in ("br", "break"):
                    break
                aname.append(sibling)
    
    def fix_div(self, root):
        for div in root.xpath("div"):
            font = div.xpath(".//font|.//span")
            if font:
                div.tag = "tostrip"
            else:
                div.tag = "p"
        ET.strip_tags(root, "tostrip")
    
    def change_font_to_p(self, root):
        for child in root.xpath("font"):
            child.tag = "p"

    def change_font_break_to_p(self, root):
        children = list(root.xpath(".//font|.//span"))
        if not children:
            return
        for child in children:
            next_sibling = child.getnext()
            if next_sibling is None:
                continue
            if next_sibling.tag in ("br", "break", "p"):
                next_sibling.tag = "tostrip"
                child.tag = "p"
        ET.strip_tags(root, "tostrip")

    def change_font_with_inner_break_to_p(self, root):
        for child in list(root.xpath(".//font[break]|.//span[break]")):
            parent = child.getparent()
            if parent.tag == "p":
                continue
            br_nodes = child.xpath("break")
            if not br_nodes:
                continue
            last_child = br_nodes[-1]
            if not is_last_item_in_parent(last_child):
                continue
            last_child.tag = "tostrip"
            child.tag = "p"
        ET.strip_tags(root, "tostrip")

    def strip_break_which_is_p_sibling(self, root):
        for br in root.xpath(".//break"):
            previous = br.getprevious()
            if previous is not None and previous.tag == "p":
                br.tag = "tostrip"
                continue
            nextsibling = br.getnext()
            if nextsibling is not None and nextsibling.tag == "p":
                br.tag = "tostrip"
                continue
        ET.strip_tags(root, "tostrip")

    def wrap_title_which_is_p_sibling(self, root):
        for title in root.xpath(".//title"):
            previous = title.getprevious()
            if previous is not None and previous.tag == "p":
                self.wrap_title(title)
                continue
            nextsibling = title.getnext()
            if nextsibling is not None and nextsibling.tag == "p":
                self.wrap_title(title)
                continue

    def wrap_title(self, title):
        p = ET.Element("p")
        title.addprevious(p)
        p.append(title)

    def strip_p_p(self, root):
        for p in list(root.xpath(".//p[p]")):
            if p.text and p.text.strip():
                continue
            strip = True
            for child in p.getchildren():
                if child.tail and child.tail.strip():
                    strip = False
                    break
            if not strip:
                continue
            p.tag = "TAGTOSTRIP"
        ET.strip_tags(root, "TAGTOSTRIP")

    # def mark_breakes_which_are_last_child(self, root):
    #     for br in root.xpath(f".//{self.break_tag}"):
    #         if not is_last_item_in_parent(br):
    #             continue
    #         br.tag = "LASTBREAK"

    # def mark_nodes_which_should_be_p(self, root):
    #     for child in root.getchildren():
    #         br_nodes = child.xpath(f".//LASTBREAK")
    #         if not br_nodes:
    #             continue
    #         if len(br_nodes) > 1:
    #             continue
    #         br_node = br_nodes[0]
    #         if not self.find_last_child_and_check_is_last_break(child):
    #             continue
    #         br_node.tag = "TAGTOSTRIP"
    #         child.set("tag", "p")
    #     ET.strip_tags(root, "TAGTOSTRIP")

    # def find_last_child_and_check_is_last_break(self, parent):
    #     if parent.tag == "LASTBREAK":
    #         return True
    #     children = parent.getchildren()
    #     if not children:
    #         return False
    #     return self.find_last_child_and_check_is_last_break(children[-1])

    # def mark_br_parents(self, root):
    #     for br_parent in list(root.xpath(f".//*[{self.break_tag}]")):
    #         br_parent.tag = "br-parent"

    # def create_p_in_br_parents(self, root):
    #     for br_parent in list(root.xpath(".//br-parent")):
    #         self.create_p_in_br_parent(br_parent)

    # def create_p_in_br_parent(self, parent):
    #     children = list(parent.getchildren())
    #     p = None
    #     if parent.text and parent.text.strip():
    #         p = ET.Element("p")
    #         parent.insert(0, p)
    #         p.text = parent.text
    #         parent.text = None
    #     for item in children:
    #         if item.tag in ("br", "break"):
    #             item.tag = "p"
    #             p = item
    #             if p.tail and p.tail.strip():
    #                 p.text = p.tail
    #                 p.tail = None
    #             continue
    #         # item != br | break
    #         if p is None:
    #             p = ET.Element("p")
    #             item.addprevious(p)
    #         p.append(item)


class MoveBoldPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        self.mark_todo(xml)
        self.move_bold_tags(xml)
        return data

    def mark_todo(self, xml):
        for item in list(xml.xpath(".//bold[*]")):
            item.tag = "TODOTAG"

    def move_bold_tags(self, xml):
        while True:
            bold_nodes = xml.xpath(".//TODOTAG")
            if not bold_nodes:
                break
            self.move_bold_tag(bold_nodes[0])

    def move_bold_tag(self, bold):
        for child in list(bold.getchildren()):
            text = "".join(child.xpath(".//text()")).strip()
            if not text:
                continue
            if child.tag in ("italic", "sup", "sub", "xref"):
                continue
            new_element = ET.Element(child.tag)
            child.addprevious(new_element)
            child.tag = "bold"
            new_element.append(child)
        ET.strip_tags(bold, "TODOTAG")


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
        self.convert_div_break_to_p(xml)
        self.convert_div_title_to_sec(xml)
        self.strip_left_div(xml)
        return data

    def convert_div_break_to_p(self, xml):
        for node in list(xml.xpath(".//div[break]")):
            if node.find("p") is None and node.find("div") is None:
                node.tag = "p"

    def convert_div_title_to_sec(self, xml):
        for node in list(xml.xpath(".//div[title]")):
            children = list(node.getchildren())
            if not children:
                continue
            first_child = children[0]
            if first_child.tag != "title":
                continue
            node.tag = "sec"

    def strip_left_div(self, xml):
        for node in list(xml.xpath(".//div")):
            node.tag = "tostrip"
        ET.strip_tags(xml, "tostrip")


class AckPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for ack_node in xml.xpath(".//ack"):
            self.process_ack_node(ack_node)
        return data
    
    def process_ack_node(self, ack_node):
        if ack_node.xpath(".//p"):
            return
        next_node = ack_node.getnext()
        if next_node is not None and next_node.tag == "p":
            ack_node.append(next_node)


class XMLWrapTitleTailPipe(plumber.Pipe):
    def transform(self, data):
        """
        Envolve o texto que está no final do título em um elemento <p>.

        Isso é necessário porque, em alguns casos, o título pode conter
        texto adicional que não faz parte do título em si, e esse texto
        deve ser tratado como um parágrafo separado.

        A função percorre o XML do documento, identifica os elementos
        de título e verifica se há texto adicional após o título.
        Se houver, esse texto é removido do título e colocado dentro
        de um novo elemento <p> que é inserido logo após o título
        no XML
        """
        raw, xml = data
        for title in xml.xpath(".//title"):
            self.wrap_title_tail(title)
        return data
    
    def wrap_title_tail(self, title):
        if not title.tail or not title.tail.strip():
            return
        new_p = ET.Element("p")
        new_p.text = title.tail
        title.tail = ""
        title.addnext(new_p)


class ExcludeMultipleBreaksPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        breaks = xml.xpath(".//br|.//break")
        if not breaks:
            return data
        
        for br in breaks:
            self.mark_to_strip(br)
        self.strip_tags(xml)
        return data
    
    def mark_to_strip(self, br):
        if br.tail and br.tail.strip():
            return
        next_sibling = br.getnext()
        if next_sibling is None:
            return
        if next_sibling.tag != br.tag:
            return
        br.set("tostrip", "true")

    def strip_tags(self, xml):
        for node in xml.xpath(".//*[@tostrip='true']"):
            node.tag = "TAGTOSTRIP"
        ET.strip_tags(xml, "TAGTOSTRIP")


class XMLNormalizeSpacePipe(plumber.Pipe):
    """
    In [38]: xml = '<article><body><p><bold>texto bold</bold> texto pos bold</p><p2>texto in p<italic>iiiii</italic><br/>...</p2></body></article>'

    In [39]: x = etree.fromstring(xml)

    In [40]: x.xpath(".//*[text()]")
    Out[40]:
    [<Element p at 0x110aaf980>,
     <Element bold at 0x1109fb380>,
     <Element p2 at 0x1109fb500>,
     <Element italic at 0x1109fb1c0>]

    In [41]: x.xpath(".//*[following-sibling::text()[1]]")
    Out[41]:
    [<Element bold at 0x1109fb380>,
     <Element italic at 0x1109fb1c0>,
     <Element br at 0x1109f3880>]

    In [43]: x.xpath(".//*[following-sibling::text()] | .//*[text()]")
    Out[43]:
    [<Element p at 0x110aaf980>,
     <Element bold at 0x1109fb380>,
     <Element p2 at 0x1109fb500>,
     <Element italic at 0x1109fb1c0>,
     <Element br at 0x1109f3880>]
    """
    def transform(self, data):
        raw, xml = data

        # seleciona nós que tem text e/ou tail
        for node in xml.xpath(".//*[following-sibling::text()] | .//*[text()]"):
            self.process_node_text(node)
            self.process_node_tail(node)
        return data

    def process_node_text(self, node):
        if node.text:
            previous_space = ""
            posterior_space = ""
            if not node.text[0].strip():
                # há um caracter de espaço e deve ser preservado
                previous_space = node.text[0]
            if not node.text[-1].strip():
                # há um caracter de espaço e deve ser preservado
                posterior_space = node.text[-1]
            node.text = self.normalize_space(node.text, previous_space, posterior_space)

    def process_node_tail(self, node):
        if node.tail:
            previous_space = ""
            posterior_space = ""
            if not node.tail[0].strip():
                # há um caracter de espaço e deve ser preservado
                previous_space = node.tail[0]
            if not node.tail[-1].strip():
                # há um caracter de espaço e deve ser preservado
                posterior_space = node.tail[-1]
            node.tail = self.normalize_space(node.tail, previous_space, posterior_space)

    def normalize_space(self, text, previous_space, posterior_space):
        if not text:
            return text
        return previous_space + " ".join([word.strip() for word in text.split() if word.strip()]) + posterior_space

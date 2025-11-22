import traceback
import sys
import logging
import os
from copy import deepcopy
from io import StringIO
import re

import plumber
from lxml import etree as ET
from scielo_classic_website.htmlbody.html_body import HTMLContent
from scielo_classic_website.spsxml.sps_xml_article_meta import XMLNormalizeSpacePipe
from scielo_classic_website.utils.body_sec_type_matcher import get_sectype
from scielo_classic_website.htmlbody.name2number import fix_pre_loading


REF_TYPES = {
    "t": "table",
    "f": "fig",
    "e": "disp-formula",
}

LABEL_INITIAL_TO_ELEMENT = {
    "t": "table-wrap",
    "f": "fig",
    "e": "disp-formula",
    "c": "table-wrap", # cuadro
    "a": "app", # appendix, anexo
}

FILENAME_TO_ELEMENT = {}
FILENAME_TO_ELEMENT.update(LABEL_INITIAL_TO_ELEMENT)
FILENAME_TO_ELEMENT["i"] = "fig"


ELEM_AND_REF_TYPE = {
    "table-wrap": "table",
}


def get_letter_and_number(codigo):
    """
    Verifica se a string inteira corresponde exatamente ao padrão:
    [Letra (maiúscula/minúscula)][Um ou mais dígitos].
    Se corresponder (ex: 'f1', 'A99'), retorna a string original.
    Se não corresponder (ex: '1f', 'f1a'), retorna None.
    """
    
    # Expressão Regular: r"^[a-zA-Z]\d+$"
    # ^: Início da string
    # [a-zA-Z]: Exatamente uma letra
    # \d+: Um ou mais dígitos
    # $: Fim da string
    regex = r"^[a-zA-Z]\d+$"
    
    # re.fullmatch() verifica se a string inteira corresponde ao padrão
    match = re.fullmatch(regex, codigo)
    
    if match:
        # Se o padrão casar com a string inteira, retorna o valor original
        return codigo
    else:
        # Caso contrário, retorna None
        return None


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
    if not children_data_as_text:
        return None
    try:
        fixed = fix_pre_loading(children_data_as_text)
        if element_name == "body":
            html_content = fixed
        else:
            html_content = f"<{element_name}>{fixed}</{element_name}>"
        return ET.fromstring(html_content)
    except Exception as e:
        pass
    try:
        hc = HTMLContent(html_content)
        return hc.tree.find(f".//{element_name}")
    except Exception as e:
        logging.exception(e)
        logging.info(element_name)
        logging.info(children_data_as_text)

        raise Exception(f"Error: text_to_node {element_name} {children_data_as_text}")


def convert_html_to_xml(document):
    """
    document está em scielo_classic_website.models.document.Document.
    """
    calls = (
        convert_html_to_xml_step_0,
        convert_html_to_xml_step_1,
        convert_html_to_xml_step_2,
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


def convert_html_to_xml_step_0(document):
    """
    Coloca os textos HTML principal e traduções na estrutura do XML:
    article/body, article/back/ref-list, article/back/sec,
    sub-article/body, sub-article/back,

    Parameters
    ----------
    document: Document
    """
    # logging.info("convert_html_to_xml - step 1")
    ppl = plumber.Pipeline(
        SetupPipe(),
        PreMainHTMLPipe(),
        PreTranslatedHTMLPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_1(document):
    """
    Coloca os textos HTML principal e traduções na estrutura do XML:
    article/body, article/back/ref-list, article/back/sec,
    sub-article/body, sub-article/back,

    Parameters
    ----------
    document: Document
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


def convert_html_to_xml_step_2(document):
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


def convert_html_to_xml_step_3(document):
    """
    Converte o XML obtido no passo 2.
    Localiza os xref e os graphics e adiciona, respectivamente, ref-type e
    os elementos fig, table-wrap, disp-formula, de acordo como o nome / local.

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
    # logging.info("convert_html_to_xml - step 3")
    ppl = plumber.Pipeline(
        StartPipe(),
        XRefSpecialInternalLinkPipe(),
        InlineGraphicPipe(),
        # RemoveParentPTagOfGraphicPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_4(document):
    """
    Converte o XML obtido no passo 3,

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
    # logging.info("convert_html_to_xml - step 4")
    ppl = plumber.Pipeline(
        StartPipe(),
        DivIdToAssetPipe(),
        XRefTypePipe(),
        InsertGraphicInFigPipe(),
        RemoveEmptyPTagPipe(),
        InsertGraphicInTableWrapPipe(),
        RemoveEmptyPTagPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_5(document):
    """
    Converte o XML obtido no passo 4,

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
    Converte o XML obtido no passo 6,

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
    ppl = plumber.Pipeline(
        StartPipe(),
        AlternativesGraphicPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_fix_body(document):
    ppl = plumber.Pipeline(
        StartPipe(),
        WrapPwithSecPipe(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_complete_disp_formula(document):
    # logging.info("convert_html_to_xml - step 5")
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
            parent.remove(item)
            node = text_to_node("mixed-citation", item.text)
            if node.getchildren() and not (node.tail or "").strip():
                node = node.find("*")
                node.tag = "mixed-citation"
            parent.append(node)
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
        for br_parent in body.xpath(f"*[{break_tag}]"):
            if len(br_parent.xpath(break_tag)) == 1:
                continue
            # Coletar o conteúdo e criar novos parágrafos
            new_elements = []
            p = ET.Element("p")

            # Adicionar texto inicial se existir
            if br_parent.text:
                p.text = br_parent.text
                br_parent.text = None

            # Processar cada filho
            for (
                child
            ) in (
                br_parent.getchildren()
            ):  # usar list() para evitar modificar durante iteração
                if child.tag == break_tag:
                    # Adicionar parágrafo atual se tiver conteúdo
                    if p.text or len(p):
                        new_elements.append(p)
                    # Criar novo parágrafo
                    p = ET.Element("p")
                    if child.tail:
                        p.text = child.tail
                else:
                    # Adicionar elemento não-break ao parágrafo atual
                    p.append(child)

            # Adicionar último parágrafo se tiver conteúdo
            if p.text or len(p):
                new_elements.append(p)

            # Limpar o parent original
            br_parent.clear()

            # Adicionar os novos elementos
            for elem in new_elements:
                br_parent.addprevious(elem)


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
            if not node.get("style"):
                continue
            for style in ("italic", "sup", "sub", "bold", "underline"):
                if style in node.get("style"):
                    node.tag = style
                    node.attrib.pop("style")
                    break
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
    def _create_ext_link(self, node, extlinktype="uri"):
        node.tag = "ext-link"
        href = (node.get("href") or "").strip()
        node.attrib.clear()
        node.set("ext-link-type", extlinktype)
        node.set("{http://www.w3.org/1999/xlink}href", href)

    def _create_email(self, node):
        email_from_href = None
        email_from_node_text = None

        node.tag = "email"
        href = (node.get("href") or "").strip()
        node.attrib.clear()

        texts = href.replace("mailto:", "")
        for text in texts.split():
            if "@" in text:
                email_from_href = text
                break

        texts = (node.text or "").strip()
        for text in texts.split():
            if "@" in text:
                email_from_node_text = text
                break
        node.text = email_from_href or email_from_node_text

    def _create_internal_link(self, node):
        node.tag = "xref"
        try:
            xml = ET.tostring(node)
            node.set("rid", node.attrib.pop("href")[1:].lower())
        except (ValueError, TypeError, AttributeError, IndexError) as e:
            logging.error(f"Unable to _create_internal_link for {xml}")
            logging.exception(e)

    def _create_internal_link_to_asset_html_page(self, node):
        node.tag = "xref"
        node.set("is_internal_link_to_asset_html_page", "true")

    def parser_node(self, node, journal_acron):
        href = node.get("href") or ""
        if href.count('"') == 2:
            node.set("href", href.replace('"', ""))

        node.set("href", (node.get("href") or "").strip())
        href = node.get("href")

        if not href:
            return

        if ("mailto" in href) or (node.text and "@" in node.text):
            return self._create_email(node)

        if href[0] == "#":
            return self._create_internal_link(node)

        if "img/revistas/" in href or ".." in href:
            return self._create_internal_link_to_asset_html_page(node)

        if journal_acron and f"/{journal_acron}/" in href.lower():
            return self._create_internal_link_to_asset_html_page(node)

        if ":" in href:
            return self._create_ext_link(node)
        if "www" in href:
            return self._create_ext_link(node)
        if href.startswith("http"):
            return self._create_ext_link(node)
        href = href.split("/")[0]
        if href and href.count(".") and href.replace(".", ""):
            return self._create_ext_link(node)

    def transform(self, data):
        raw, xml = data

        for node in xml.xpath(".//a[@href]"):
            try:
                journal_acron = f"/{raw.journal.acronym}/"
            except Exception:
                journal_acron = None
            self.parser_node(node, journal_acron)
        _report(xml, func_name=type(self))
        return data


class ANamePipe(plumber.Pipe):
    def remove_top_and_back(self, root):

        for node in root.xpath(".//a[@name]"):
            name = node.get("name")
            if name.startswith("top") or name.startswith("back"):
                node.set("delete", "true")

                for ahref in root.xpath(f".//a[@href='#{name}']"):
                    ahref.set("delete", "true")
        delete_tags(root)
        # else:
        #     node.tag = "div"
        #     node.set("id", node.attrib.pop("name"))

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
            node.tag = "div"
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


class XRefTypePipe(plumber.Pipe):

    def parser_node(self, node, xml):
        rid = node.get("rid")
        if not rid:
            logging.warning("Missing rid: {}".format(ET.tostring(node)))
            return

        related = xml.find(f".//*[@id='{rid}']")
        if related is None:
            logging.warning("Missing id={}".format(rid))
            return

        node.set("ref-type", ELEM_AND_REF_TYPE.get(related.tag) or related.tag)

    def transform(self, data):
        raw, xml = data
        for xref in xml.xpath(".//xref"):
            if xref.get("ref-type"):
                continue
            self.parser_node(xref, xml)
        return data


class XRefSpecialInternalLinkPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        for xref_parent in xml.xpath(".//*[xref]"):
            if xref_parent.xpath("xref[@is_internal_link_to_asset_html_page]"):
                self.parser_xref_parent(
                    xref_parent,
                    xml,
                    raw.filename_without_extension,
                )
        _report(xml, func_name=type(self))
        return data

    def _extract_xref_text(self, xref_element):
        return " ".join(xref_element.xpath(".//text()")).strip()

    def get_rid_from_xref_label_and_number(self, label_text, label_number):
        """
        Gera o rid a partir do label_text e label_number.

        Args:
            label_text: Texto do label (e.g., 'Table', 'Figure')
            label_number: Número do label (e.g., '1', '2')

        Returns:
            String com o rid ou None
        """
        if not label_text:
            return None
        
        element_prefix = label_text[0].lower()
        if not label_number:
            return element_prefix

        if label_number.isdigit():
            return f"{element_prefix}{label_number}"
        
        if label_number[:-1].isdigit() and  label_number[-1].isalpha():
            return f"{element_prefix}{label_number[:-1]}"
        return None

    def get_rid_from_href_and_pkg_name(self, href, pkg_name):
        """
        Extrai o rid a partir do href e nome do pacote.

        Args:
            href: String com o caminho href
            pkg_name: Nome do pacote

        Returns:
            String com o rid ou None
        """
        basename = os.path.basename(href)
        filename, _ = os.path.splitext(basename)
        if filename.startswith(pkg_name):
            filename = filename.replace(pkg_name, "")
            if not filename:
                return None
        return get_letter_and_number(filename)

    def _extract_filename(self, href):
        basename = os.path.basename(href)
        filename, ext = os.path.splitext(basename)
        return filename, ext

    def get_label_text_and_number_from_xref_text(self, xref_text, label_text):
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
                return label_text, expected_number
        return parts[0], None
    
    def get_element_name(self, label_text, rid, ext):
        element_name = None
        if label_text:
            label_initial = label_text[0].lower()
            element_name = LABEL_INITIAL_TO_ELEMENT.get(label_initial)
        elif rid:
            element_name = FILENAME_TO_ELEMENT.get(rid[0])
        if not element_name:
            if ext in (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".html", ".htm"):
                element_name = "supplementary-material"
        if not element_name:
            element_name = "element"
        return element_name

    def parser_xref_parent(self, xref_parent, root, pkg_name):
        label_text = None
        children = []

        for child in xref_parent.xpath(
            "xref[@is_internal_link_to_asset_html_page and @href]"
        ):

            # Table 1
            xref_text = self._extract_xref_text(child)
            if not xref_text:
                logging.error("XRefSpecialInternalLinkPipe - no xref_text found")
                continue
            try:
                href = child.attrib.pop("href")
            except KeyError:
                logging.error("XRefSpecialInternalLinkPipe - no href found")
                continue

            basename, ext = self._extract_filename(href)
            child.set("filebasename", basename)

            label_text, label_number = self.get_label_text_and_number_from_xref_text(xref_text, label_text)
            rid = self.get_rid_from_xref_label_and_number(label_text, label_number)
            if not rid:
                rid = self.get_rid_from_href_and_pkg_name(href, pkg_name)
            if rid:
                child.set("rid", rid)

            element_name = self.get_element_name(label_text, rid, ext)
            try:
                xpath = f"//*[@filebasename='{basename}']"
                if rid:
                    xpath = f"//*[@id='{rid}' | @filebasename='{basename}']"
                found = root.xpath(xpath)[0]
                if not found.get("filebasename"):
                    found.set("filebasename", basename)
                if not found.get("id") and rid:
                    found.set("id", rid)
                
            except IndexError:
                new_elem = ET.Element(element_name)
                if rid:
                    new_elem.set("id", rid)
                new_elem.set("filebasename", basename)

                elem_label = ET.Element("label")
                new_elem.append(elem_label)
                elem_label.text = xref_text

                g = ET.Element("graphic")
                g.set("{http://www.w3.org/1999/xlink}href", href)

                new_elem.append(g)
                children.append(new_elem)

            child.attrib.pop("is_internal_link_to_asset_html_page")

        # Sort children by rid before inserting
        children_sorted = sorted(children, key=lambda x: x.get("filebasename"))
        for child in children_sorted:
            node = ET.Element(xref_parent.tag)
            node.append(child)
            xref_parent.addnext(node)


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
                parent = item.getparent()
                parent.remove(item)
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
                parent.remove(item)

        for parent in xml.xpath(".//mixed-citation[break]"):
            ET.strip_tags(parent, "break")
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


class DivIdToAssetPipe(plumber.Pipe):
    """
    Transforma div em table-wrap ou fig.
    """

    def parser_node(self, node):
        attrib_id = node.get("id")
        if not attrib_id or "top" in attrib_id or "back" in attrib_id:
            return
        if attrib_id.startswith("t"):
            node.tag = "table-wrap"
        elif attrib_id.startswith("f"):
            node.tag = "fig"
        elif attrib_id.startswith("e"):
            node.tag = "disp-formula"

    def transform(self, data):
        raw, xml = data
        _process(xml, "div[@id]", self.parser_node)
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

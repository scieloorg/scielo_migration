import logging
import os
from copy import deepcopy
from io import StringIO

import plumber
from lxml import etree as ET

from scielo_classic_website.htmlbody.html_body import HTMLContent
from scielo_classic_website.spsxml.sps_xml_article_meta import XMLNormalizeSpacePipe


class XMLBodyAnBackConvertException(Exception):
    ...


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


def text_to_node(children_data_as_text):
    hc = HTMLContent(children_data_as_text)
    tree = ET.fromstring(hc.content)
    return tree.find(".")


def convert_html_to_xml(document):
    """
    document está em scielo_classic_website.models.document.Document.
    """
    calls = (
        convert_html_to_xml_step_1,
        convert_html_to_xml_step_2,
        convert_html_to_xml_step_3,
        convert_html_to_xml_step_4,
        # convert_html_to_xml_step_5,
        # convert_html_to_xml_step_6,
        # convert_html_to_xml_step_7,
    )
    document.xml_body_and_back = []
    try:
        for i, call_ in enumerate(calls, start=1):
            document.xml_body_and_back.append(call_(document))
    except Exception as e:
        raise XMLBodyAnBackConvertException(
            f"convert_html_to_xml (step {i}): {type(e)} {e}"
        )


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
        SetupPipe(),
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
        RemoveHTMLTagsPipe(),
        RenameElementsPipe(),
        StylePipe(),
        RemoveSpanTagsPipe(),
        OlPipe(),
        UlPipe(),
        TagsHPipe(),
        ASourcePipe(),
        AHrefPipe(),
        ANamePipe(),
        ImgSrcPipe(),
        RemoveEmptyPTagPipe(),
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
        XRefFixPipe(),
        XRefTypePipe(),
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
        body = ET.Element("body")
        back = ET.Element("back")
        xml.append(body)
        xml.append(back)
        _report(xml, func_name=type(self))
        return data, xml


class EndPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        data = ET.tostring(
            xml,
            encoding="utf-8",
            method="xml",
            pretty_print=True,
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

    def transform(self, data):
        raw, xml = data

        # trata do bloco anterior às referências
        text = "".join(
            [
                item["text"]
                for item in raw.main_html_paragraphs["before references"] or []
            ]
        )
        node = text_to_node(text)
        body = xml.find(".//body")
        body.extend(node.getchildren())

        # trata do bloco das referências
        references = ET.Element("ref-list")
        for i, item in enumerate(raw.main_html_paragraphs["references"] or []):
            # item.keys() = (text, index, reference_index, part)
            # cria o elemento `ref` com conteúdo de `item['text']`,
            ref = ET.Element("ref")
            try:
                ref_index = item["reference_index"]
            except KeyError:
                ref_index = i + 1
            # cria o atributo ref/@id
            ref.set("id", f"B{ref_index}")

            # cria o elemento mixed-citation que contém o texto da referência
            # bibliográfica mantendo as pontuação
            if item["text"].strip():
                mixed_citation = text_to_node(item["text"])
                mixed_citation.tag = "mixed-citation"
            else:
                mixed_citation = ET.Element("mixed-citation")

            # adiciona o elemento que contém o texto da referência
            # bibliográfica ao elemento `ref`
            ref.append(mixed_citation)

            # adiciona `ref` ao `ref-list`
            references.append(ref)

        # busca o elemento `back`
        back = xml.find(".//back")
        back.append(references)

        text = "".join(
            [
                item["text"]
                for item in raw.main_html_paragraphs["after references"] or []
            ]
        )
        if text.strip():
            node = text_to_node(text)
            for child in node.getchildren():
                sec = ET.Element("sec")
                sec.append(child)
                back.append(sec)

        _report(xml, func_name=type(self))
        return data

        # class MainHTMLPipe(plumber.Pipe):
        #     """
        #     O texto completo principal é dividido em 3 partes
        #     - 'before references': antes das referências bibliográficas
        #     - 'references': referências bibliográficas
        #     - 'after references': após das referências bibliográficas

        #     Esta etapa espera que exista `raw.main_html_paragraphs` que é
        #     um dict com chaves: `before references`, `references`, `after references`.
        #     Os valores de `before references`, `references`, `after references`
        #     são listas de dict com chaves text, index, reference_index, part.

        #     A partir do raw.main_html_paragraphs, são preenchidos os elementos
        #     article/body, article/back e article/ref-list
        #     """

        #     def transform(self, data):
        #         raw, xml = data

        #         body = xml.find(".//body")

        #         # trata do bloco anterior às referências
        #         for item in raw.main_html_paragraphs["before references"] or []:
        #             # item.keys() = (text, index, reference_index, part)
        #             # cria o elemento `p` com conteúdo de `item['text']`,
        #             # envolvido por CDATA e adiciona em body

        #             # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
        #             # acusará erro de má formação do XML. O conteúdo do CDATA será
        #             # tratado em uma etapa futura
        #             logging.info("MainHTMLPipe")
        #             logging.info(item)
        #             p = ET.Element("p")
        #             p.text = ET.CDATA(item["text"])
        #             body.append(p)

        #         # trata do bloco das referências
        #         references = ET.Element("ref-list")
        #         for i, item in enumerate(raw.main_html_paragraphs["references"] or []):
        #             # item.keys() = (text, index, reference_index, part)
        #             # cria o elemento `ref` com conteúdo de `item['text']`,

        #             logging.info("MainHTMLPipe")
        #             logging.info(item)

        #             ref = ET.Element("ref")
        #             try:
        #                 ref_index = item["reference_index"]
        #             except KeyError:
        #                 ref_index = i + 1
        #             # cria o atributo ref/@id
        #             ref.set("id", f"B{ref_index}")

        #             # cria o elemento mixed-citation que contém o texto da referência
        #             # bibliográfica mantendo as pontuação
        #             mixed_citation = ET.Element("mixed-citation")

        #             # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
        #             # acusará erro de má formação do XML. O conteúdo do CDATA será
        #             # tratado em uma etapa futura
        #             mixed_citation.text = ET.CDATA(item["text"])

        #             # adiciona o elemento que contém o texto da referência
        #             # bibliográfica ao elemento `ref`
        #             ref.append(mixed_citation)

        #             # adiciona `ref` ao `ref-list`
        #             references.append(ref)

        #         # busca o elemento `back`
        #         back = xml.find(".//back")
        #         back.append(references)
        #         for item in raw.main_html_paragraphs["after references"] or []:
        #             # item.keys() = (text, index, reference_index, part)

        #             # elementos aceitos em `back`
        #             # (ack | app-group | bio | fn-group | glossary | notes | sec)
        #             # uso de sec por ser mais genérico

        #             # cria o elemento `sec` para cada item do bloco de 'after references'
        #             # com conteúdo de `item['text']`
        #             sec = ET.Element("sec")
        #             sec.text = ET.CDATA(item["text"])

        #             # adiciona ao elemento `back`
        #             back.append(sec)

        #         # print("back/sec %i" % len(back.findall("sec")))

        _report(xml, func_name=type(self))  #
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

        back = xml.find(".//back")
        for lang, texts in raw.translated_html_by_lang.items():
            sub_article = ET.Element("sub-article")
            sub_article.set("article-type", "translation")
            sub_article.set("{http://www.w3.org/XML/1998/namespace}lang", lang)
            back.append(sub_article)

            body = ET.Element("body")

            # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
            # acusará erro de má formação do XML. O conteúdo do CDATA será
            # tratado em uma etapa futura

            # texts['before references'] é str
            node = text_to_node(texts["before references"])
            body.extend(node.getchildren())
            sub_article.append(body)

            if texts["after references"]:
                back = ET.Element("back")

                # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
                # acusará erro de má formação do XML. O conteúdo do CDATA será
                # tratado em uma etapa futura

                # texts['after references'] é str

                node = text_to_node(texts["after references"])
                back.extend(node.getchildren())

                sub_article.append(back)

        _report(xml, func_name=type(self))
        return data


##############################################################################


def remove_CDATA(old):
    logging.info(f"Remove CDATA {old.text}")
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
    TAGS = ["span", ]

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


class StylePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for style in ("bold", "italic", "sup", "sub", "underline"):
            xpath = f".//span[@name='style_{style}']"
            for node in xml.xpath(xpath):
                node.tag = style
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
        node.attrib.clear()

        href = (node.get("href") or "").strip()
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
        node.set("rid", node.attrib.pop("href")[1:])

    def _create_special_internal_link(self, node):
        node.tag = "xref"
        node.set("fixme", "true")

    def parser_node(self, node):
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
            return self._create_special_internal_link(node)

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
        _process(xml, "a[@href]", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class ANamePipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "div"
        node.set("id", node.attrib.pop("name"))

    def transform(self, data):
        raw, xml = data
        _process(xml, "a[@name]", self.parser_node)
        _report(xml, func_name=type(self))
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
    def parser_node(self, node):
        rid = node.get("rid")
        rid_first_char = rid[0]
        if rid_first_char == "t" and "top" not in rid:
            value = None
            for c in rid:
                if c.isdigit():
                    value = "table"
                    break
            if value:
                node.set("ref-type", "table")
        elif rid_first_char == "f":
            node.set("ref-type", "fig")
        elif rid_first_char == "e":
            node.set("ref-type", "disp-formula")

    def transform(self, data):
        raw, xml = data
        _process(xml, "xref", self.parser_node)
        _report(xml, func_name=type(self))
        return data


class XRefFixPipe(plumber.Pipe):
    def parser_node(self, node, root, params):
        pkg_name = params.get("pkg_name")
        parent = node.getparent()
        first_name = None
        first_label = None
        first_reftype = None
        children = []
        for child in parent.xpath("xref[@fixme and @href]"):
            try:
                href = child.attrib.pop("href")
            except KeyError:
                continue

            basename = os.path.basename(href)
            rid, ext = os.path.splitext(basename)
            rid = rid.replace(pkg_name, "")

            child.set("rid", rid)

            label = child.text
            if first_label is None:
                first_label = label.split()[0]
                if first_label.endswith("s"):
                    first_label = first_label[:-1]
            label_lower = label.lower()
            if label_lower[0] == "t":
                name = "table-wrap"
                child.set("ref-type", "table")
                first_reftype = "table"
            elif label_lower[0] == "f":
                name = "fig"
                child.set("ref-type", "fig")
                first_reftype = "fig"
            elif label_lower[0] == "e":
                name = "disp-formula"
                child.set("ref-type", "disp-formula")
                first_reftype = "disp-formula"
            elif label_lower[0].isdigit():
                name = first_name
                label = f"{first_label} {label}"
                if first_reftype:
                    child.set("ref-type", first_reftype)
            if first_name is None:
                first_name = name

            child.attrib.pop("fixme")
            xpath = f"//{name}[@id='{rid}']"
            if len(root.xpath(xpath)) == 0:
                new_elem = ET.Element(name)
                new_elem.set("id", rid)

                elem_label = ET.Element("label")
                elem_label.text = label
                new_elem.append(elem_label)

                g = ET.Element("graphic")
                g.set("{http://www.w3.org/1999/xlink}href", href)
                new_elem.append(g)
                children.append(new_elem)

        for child in reversed(children):
            node = ET.Element(parent.tag)
            node.append(child)
            parent.addnext(node)

    def transform(self, data):
        raw, xml = data
        try:
            params = {"pkg_name": raw.filename_without_extension}
        except AttributeError:
            params = {}

        _process_with_params(
            xml,
            "xref[@fixme]",
            self.parser_node,
            params,
        )
        _report(xml, func_name=type(self))
        return data


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
            if grand_parent.tag == "body":
                break
            parent = parent.getparent()

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
            if grand_parent.tag == "body":
                break
            parent = parent.getparent()

        sibling = parent.getnext()
        if sibling is None:
            comment = etree.Comment("FIXME check whether element is table-wrap")
            node.insert(1, comment)
            logging.info(f"Unable to find graphic for {node.get('id')}")
            return
        table = sibling.find(".//table")
        graphic = sibling.find(".//graphic")
        if graphic is None and table is None:
            return
        if graphic is not None:
            node.append(deepcopy(graphic))
            elem = graphic
        elif table is not None:
            node.append(deepcopy(table))
            elem = table
        parent = elem.getparent()
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

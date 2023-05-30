import logging
from io import StringIO

import plumber
from lxml import etree as ET


def convert_html_to_xml(document):
    """
    document está em scielo_classic_website.models.document.Document.
    """

    document.xml_body_and_back = []
    document.xml_body_and_back.append(convert_html_to_xml_step_1(document))
    document.xml_body_and_back.append(convert_html_to_xml_step_2(document))
    document.xml_body_and_back.append(convert_html_to_xml_step_3(document))
    document.xml_body_and_back.append(convert_html_to_xml_step_4(document))
    # document.xml_body_and_back.append(convert_html_to_xml_step_5(document))


def convert_html_to_xml_step_1(document):
    """
    Coloca os textos HTML principal e traduções na estrutura do XML:
    article/body, article/back/ref-list, article/back/sec,
    sub-article/body, sub-article/back,
    e inserindo o conteúdo em CDATA

    Parameters
    ----------
    document: Document
    """
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
    remove o conteúdo de CDATA e converte as tags HTML nas XML correspondentes
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
    ppl = plumber.Pipeline(
        StartPipe(),
        RemoveCDATAPipe(),
        RemoveCommentPipe(),
        FontSymbolPipe(),
        RemoveTagsPipe(),
        RenameElementsPipe(),
        StylePipe(),
        OlPipe(),
        UlPipe(),
        TagsHPipe(),
        ASourcePipe(),
        AHrefPipe(),
        ANamePipe(),
        ImgSrcPipe(),
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
    ppl = plumber.Pipeline(
        StartPipe(),
        XRefTypePipe(),
        RemoveEmptyPTagPipe(),
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
    ppl = plumber.Pipeline(
        StartPipe(),
        DivIdToTableWrap(),
        InsertGraphicInTableWrap(),
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
    ppl = plumber.Pipeline(
        StartPipe(),
        InsertGraphicInTableWrap(),
        EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def _process(xml, tag, func):
    nodes = xml.findall(".//%s" % tag)
    for node in nodes:
        func(node)


class StartPipe(plumber.Pipe):
    """
    raw.xml_body_and_back é o atributo que guarda os resultados
    de cada conversão do HTML para o XML

    Esta etapa pega o resultado da última conversão feita
    e aplica novas conversões
    """

    def transform(self, data):
        raw = data
        xml = ET.fromstring(raw.xml_body_and_back[-1])
        return data, xml


class SetupPipe(plumber.Pipe):
    def precond(data):
        raw = data
        logging.info(type(raw))
        logging.info(type(raw.main_html_paragraphs))
        if not raw.main_html_paragraphs["before references"]:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
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
        return data, xml


class EndPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        data = ET.tostring(
            xml,
            encoding="utf-8",
            method="xml",
        )
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

        body = xml.find(".//body")

        # trata do bloco anterior às referências
        for item in raw.main_html_paragraphs["before references"] or []:
            # item.keys() = (text, index, reference_index, part)
            # cria o elemento `p` com conteúdo de `item['text']`,
            # envolvido por CDATA e adiciona em body

            # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
            # acusará erro de má formação do XML. O conteúdo do CDATA será
            # tratado em uma etapa futura
            p = ET.Element("p")
            p.text = ET.CDATA(item["text"])
            body.append(p)

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
            mixed_citation = ET.Element("mixed-citation")

            # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
            # acusará erro de má formação do XML. O conteúdo do CDATA será
            # tratado em uma etapa futura
            mixed_citation.text = ET.CDATA(item["text"])

            # adiciona o elemento que contém o texto da referência
            # bibliográfica ao elemento `ref`
            ref.append(mixed_citation)

            # adiciona `ref` ao `ref-list`
            references.append(ref)

        # busca o elemento `back`
        back = xml.find(".//back")
        back.append(references)
        for item in raw.main_html_paragraphs["after references"] or []:
            # item.keys() = (text, index, reference_index, part)

            # elementos aceitos em `back`
            # (ack | app-group | bio | fn-group | glossary | notes | sec)
            # uso de sec por ser mais genérico

            # cria o elemento `sec` para cada item do bloco de 'after references'
            # com conteúdo de `item['text']`
            sec = ET.Element("sec")
            sec.text = ET.CDATA(item["text"])

            # adiciona ao elemento `back`
            back.append(sec)

        # print("back/sec %i" % len(back.findall("sec")))

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
            body.text = ET.CDATA(texts["before references"])
            sub_article.append(body)

            if texts["after references"]:
                back = ET.Element("back")

                # O CDATA evita que o seu conteúdo seja "parseado" e, assim não
                # acusará erro de má formação do XML. O conteúdo do CDATA será
                # tratado em uma etapa futura

                # texts['after references'] é str
                back.text = ET.CDATA(texts["after references"])
                sub_article.append(back)

        return data


##############################################################################


def html_body_tree(html_text):
    # html_text = "<html><head><title>test<body><h1>page title</h3>"
    try:
        parser = ET.HTMLParser()
        h = ET.parse(StringIO(html_text), parser)
        return h.getroot().find(".//body")
    except AttributeError:
        logging.info("html_body_tree: %s" % html_text)
        return None


def remove_CDATA(old):
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
        return data


class RemoveTagsPipe(plumber.Pipe):
    TAGS = ["font", "small", "big", "span", "s", "lixo", "center"]

    def transform(self, data):
        raw, xml = data
        ET.strip_tags(xml, self.TAGS)
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
        ("i", "italic"),
    )

    def transform(self, data):
        raw, xml = data

        for old, new in self.from_to:
            xpath = f".//{old}"
            for node in xml.findall(xpath):
                node.tag = new
        return data


class FontSymbolPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        xpath = f".//font[@face='symbol']"
        for node in xml.xpath(xpath):
            node.tag = "font-face-symbol"
        return data


class StylePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for style in ("bold", "italic", "sup", "sub", "underline"):
            xpath = f".//span[@name='style_{style}']"
            for node in xml.xpath(xpath):
                node.tag = style
        return data


class OlPipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "list"
        node.set("list-type", "order")

    def transform(self, data):
        raw, xml = data
        _process(xml, "ol", self.parser_node)
        return data


class UlPipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "list"
        node.set("list-type", "bullet")
        node.attrib.pop("list", None)

    def transform(self, data):
        raw, xml = data
        _process(xml, "ul", self.parser_node)
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

        if href[0] in ["#", "."] or "/img/revistas/" in href or ".." in href:
            return self._create_internal_link(node)

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
        return data


class ANamePipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "div"
        node.set("id", node.attrib.pop("name"))

    def transform(self, data):
        raw, xml = data
        _process(xml, "a[@name]", self.parser_node)
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
        return data


class XRefTypePipe(plumber.Pipe):
    def parser_node(self, node):
        rid_first_char = node.get("rid")[0]
        if rid_first_char == "t":
            node.set("ref-type", "table")
        elif rid_first_char == "f":
            node.set("ref-type", "fig")

    def transform(self, data):
        raw, xml = data
        _process(xml, "xref", self.parser_node)
        return data


class FigPipe(plumber.Pipe):
    """
    Envolve o elemento graphic dentro de fig.

    Resultado esperado:

    <fig id="f1">
        <graphic xlink:href="f1.jpg"/>
    </fig>
    """

    def parser_node(self, node):
        parent = node.getparent()

        for sibling in parent.itersiblings():
            if sibling.tag != "p":
                continue

            if sibling.find("graphic") is not None:
                graphic = sibling.find("graphic")
                node.append(graphic)

                parent_node = sibling.getparent()
                parent_node.remove(sibling)
                break

    def transform(self, data):
        raw, xml = data
        _process(xml, "fig[@id]", self.parser_node)
        return data


class InsertGraphicInTableWrap(plumber.Pipe):
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
        parent = node.getparent()

        for sibling in parent.itersiblings():
            if sibling.tag == "p":
                if sibling.find("graphic") is not None:
                    graphic = sibling.find("graphic")
                    node.append(graphic)
                    break
                elif sibling.find("table") is not None:
                    table = sibling.find("table")
                    node.append(table)
                    break

    def transform(self, data):
        raw, xml = data
        _process(xml, "table-wrap[@id]", self.parser_node)
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
        if node.text.strip():
            return None

        tail = node.tail
        parent = node.getparent()
        parent.remove(node)

        # Adiciona o tail no parent.
        parent.text = tail

    def transform(self, data):
        raw, xml = data
        _process(xml, "p", self.parser_node)
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
        node.tag = "inline-graphic"

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
        return data


class DivIdToTableWrap(plumber.Pipe):
    """
    Transforma div em table-wrap ou fig.
    """

    def parser_node(self, node):
        attrib_id = node.get("id")
        if attrib_id and attrib_id.startswith("t") and attrib_id != "top":
            node.tag = "table-wrap"
        elif attrib_id and attrib_id.startswith("f"):
            node.tag = "fig"

    def transform(self, data):
        raw, xml = data
        _process(xml, "div[@id]", self.parser_node)
        return data

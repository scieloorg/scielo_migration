import logging
import os
from functools import cached_property

from lxml import etree

from scielo_classic_website.htmlbody import html_fixer
from scielo_classic_website.htmlbody.name2number import fix_pre_loading


class UnableToGetHTMLTreeError(Exception): ...


class HTMLContent:
    """
    >>> from scielo_classic_website.htmlbody.html_body import HTMLContent
    >>> hc = HTMLContent("<root><p>&nbsp;&ntilde;&#985;<br><hr><img src='x.gif'></root>")
    >>> hc.content
    >>> '<root><p>\xa0ñϙ<br/></p><hr/><img src="x.gif"/></root>'
    """

    def __init__(self, content):
        self.original = content
        self.best_choice = None
        self.score = 0
        self.fixed_html = None
        self._tree = None

        try:
            self.fixed_html = html_fixer.get_fixed_html(content)
            self.score = html_fixer.get_fixed_similarity_rate(
                self.original, self.fixed_html
            )
            self.best_choice = html_fixer.get_best_choice_between_original_and_fixed(
                self.score, self.original, self.fixed_html
            )
            if self.best_choice == "original":
                self.tree = self.original
            else:
                self.tree = self.fixed_html
        except Exception as e:
            logging.exception(e)
            logging.info((self.score, self.best_choice))
            self.tree = self.original

    @staticmethod
    def create(file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            with open(file_path, encoding="iso-8859-1") as f:
                text = f.read()
        return HTMLContent(text)

    @property
    def content(self):
        if self.tree is None:
            logging.info("returning original content")
            return self.original
        try:
            self.fix_asset_paths()
            return html_fixer.html2xml(self.tree)
        except Exception as e:
            logging.exception(e)
            logging.info(f"returning original content due to exception: {e}")
            return self.original

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, content):
        self._tree = html_fixer.load_html(content)

    @property
    def asset_path_fixes(self):
        return {item["old_link"]: item["new_link"] for item in self.old_and_new_links}

    @property
    def old_and_new_links(self):
        if self.tree is None:
            return []

        for elem, attr in (("img", "src"), ("a", "href")):
            for node in self.tree.xpath(f"//{elem}[@{attr}]"):
                old_link = node.get(attr)
                if not old_link:
                    continue
                if ":" in old_link:
                    continue
                new_link = os.path.realpath(old_link)
                if not os.path.isfile(new_link):
                    continue

                for folder in ("htdocs", "bases"):
                    if folder not in new_link:
                        continue
                    new_link = new_link[new_link.find(folder) + len(folder) :]
                    logging.info({"old_link": old_link, "new_link": new_link})
                    yield {"old_link": old_link, "new_link": new_link}
                    break

    def fix_asset_paths(self):
        if self.tree is None:
            return
        for change in self.old_and_new_links:
            old_link = change.get("old_link")
            new_link = change.get("new_link")
            for node in self.tree.xpath(
                f'.//a[@href="{old_link}"]|.//img[@src="{old_link}"]'
            ):
                if node.get("href"):
                    attr = "href"
                elif node.get("src"):
                    attr = "src"
                logging.info(f"old {old_link} => new {new_link}")
                node.set("data-old-link", old_link)
                node.set(attr, new_link)


class BodyFromISIS:
    """
    Interface amigável para obter os dados da base isis
    que estão no formato JSON
    """

    def __init__(self, p_records):
        self.first_reference = None
        self.last_reference = None
        self.p_records = p_records or []
        self._identify_references_range()

    @cached_property
    def before_references_paragraphs(self):
        if self.first_reference:
            return self.p_records[: self.first_reference]
        return self.p_records

    @cached_property
    def references_paragraphs(self):
        if self.first_reference and self.last_reference:
            return self.p_records[self.first_reference : self.last_reference + 1]
        return []

    @cached_property
    def after_references_paragraphs(self):
        if self.last_reference:
            return self.p_records[self.last_reference + 1 :]
        return []

    def _identify_references_range(self):
        for i, item in enumerate(self.p_records):
            if item.reference_index:
                self.last_reference = i
                if self.first_reference:
                    continue
                self.first_reference = i

    @cached_property
    def parts(self):
        if not self.p_records:
            return {}
        parts = {}
        parts["before references"] = get_text_block(self.before_references_paragraphs)
        parts["references"] = self.get_references_block()
        parts["after references"] = get_text_block(self.after_references_paragraphs)
        return parts

    def get_references_block(self):
        references = self.references_paragraphs
        if not references:
            return []
        try:
            return list(fix_references(references))
        except Exception as e:
            # logging.exception(e)
            return list(get_paragraphs_data(references))


def get_paragraphs_text(p_records):
    for item in p_records:
        if not item.paragraph_text:
            continue
        yield item.paragraph_text


def get_text_block(paragraphs):
    if not paragraphs:
        return ""
    # corrige o bloco de parágrafos de uma vez
    return "".join(get_paragraphs_text(paragraphs))

    # hc = HTMLContent(paragraphs_text)
    # return hc.content
    # except Exception as e:
    #     # corrige cada parágrafo individualmente
    #     return get_text(get_paragraphs_data(paragraphs))

    
def get_paragraphs_data(p_records, part_name=None):
    index = None
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if not item.paragraph_text:
            continue

        if index:
            index += 1
        elif item.reference_index:
            index = int(item.reference_index)

        data = {}
        data.update(item.data)

        hc = HTMLContent(item.paragraph_text)
        data["text"] = hc.content
        if not item.reference_index:
            data["guessed_reference_index"] = str(index)
        yield data


def get_text(items):
    if not items:
        return ""
    return "".join([item["text"] for item in items or []])


def build_text(p_records):
    if not p_records:
        return ""
    document = "".join(fix_paragraphs(p_records))
    if not document:
        return ""
    hc = HTMLContent(document)
    hc.fix_asset_paths()
    return hc.content


def fix_paragraphs(p_records):
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        text = item.paragraph_text
        if text:
            yield html_fixer.avoid_mismatched_tags(text)


def fix_references(p_records):
    index = 0
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        text = (item.paragraph_text or "").strip()
        if not text:
            continue
        node = html_to_node("mixed-citation", text)
        node_text = etree.tostring(node, encoding="utf-8").decode("utf-8")
        fixed_text = node_text.replace("<mixed-citation>", "").replace("</mixed-citation>", "").strip()
        if not fixed_text:
            continue
        index += 1
        data = {}
        data.update(item.data)
        if not item.reference_index:
            data["guessed_reference_index"] = str(index)
        yield data


def html_to_node(element_name, children_data_as_text):
    if not element_name:
        raise ValueError("element_name cannot be empty")
    if not children_data_as_text:
        return etree.Element(element_name)

    # padroniza entidades
    fixed_html_entities = fix_pre_loading(children_data_as_text)
    try:
        return get_node_from_standardized_html(element_name, fixed_html_entities)
    except Exception as e:
        logging.exception(f"Tentativa 2: Error: {e}")
        xml = html_fixer.remove_tags(fixed_html_entities, ["a", "img"])
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

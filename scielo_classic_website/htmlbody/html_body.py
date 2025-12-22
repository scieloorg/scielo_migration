import logging
import os
import sys
from difflib import unified_diff
from functools import cached_property
from datetime import datetime

from lxml import etree
from lxml.etree import ParseError, register_namespace
from lxml.html import fromstring, html_to_xhtml, iterlinks, rewrite_links, tostring

from scielo_classic_website.htmlbody import html_fixer
from scielo_classic_website.htmlbody.html_code_utils import html_safe_decode


class UnableToGetHTMLTreeError(Exception): ...


class HTMLContent:
    """
    >>> from scielo_classic_website.htmlbody.html_body import HTMLContent
    >>> hc = HTMLContent("<root><p>&nbsp;&ntilde;&#985;<br><hr><img src='x.gif'></root>")
    >>> hc.content
    >>> '<root><p>\xa0ñϙ<br/></p><hr/><img src="x.gif"/></root>'
    """

    def __init__(self, content):
        # for prefix, uri in HTML_WORD_NAMESPACES.items():
        #     register_namespace(prefix, uri)
        self.original = content
        self.fixed_or_original = html_fixer.get_html_fixed_or_original(content)
        self.tree = self.fixed_or_original

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
            return self.original
        try:
            self.fix_asset_paths()
            return html_fixer.html2xml(self.tree)
        except Exception as e:
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
    if not p_records:
        return ""
    texts = []
    for item in p_records:
        if not item.paragraph_text:
            continue
        texts.append(item.paragraph_text)
    return "".join(texts)


def get_text_block(paragraphs):
    if not paragraphs:
        return ""
    try:
        # corrige o bloco de parágrafos de uma vez
        paragraphs_text = get_paragraphs_text(paragraphs)
        hc = HTMLContent(paragraphs_text)
        return hc.content
    except Exception as e:
        # corrige cada parágrafo individualmente
        return get_text(get_paragraphs_data(paragraphs))


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
    index = None
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if index:
            index += 1
        elif item.reference_index:
            index = int(item.reference_index)
        text = item.paragraph_text
        if text:
            data = {}
            data.update(item.data)
            data["text"] = html_fixer.avoid_mismatched_tags(text)
            if not item.reference_index:
                data["guessed_reference_index"] = str(index)
            yield data

import logging
import os
import sys
from difflib import unified_diff
from functools import lru_cache
from datetime import datetime

from lxml import etree
from lxml.etree import ParseError, register_namespace
from lxml.html import fromstring, html_to_xhtml, iterlinks, rewrite_links, tostring

from scielo_classic_website.htmlbody import html_fixer
from scielo_classic_website.htmlbody.html_code_utils import html_safe_decode


class UnableToGetHTMLTreeError(Exception):
    ...


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
                    new_link = new_link[
                        new_link.find(folder) + len(folder) :
                    ]
                    logging.info({"old_link": old_link, "new_link": new_link})
                    yield {"old_link": old_link, "new_link": new_link}
                    break

    def fix_asset_paths(self):
        if self.tree is None:
            return
        for change in self.old_and_new_links:
            old_link = change.get("old_link")
            new_link = change.get("new_link")
            for node in self.tree.xpath(f".//a[@href={old_link}]|.//img[@src={old_link}]"):
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

    @property
    @lru_cache(maxsize=1)
    def before_references_paragraphs(self):
        if self.p_records and self.first_reference:
            return self.p_records[: self.first_reference]
        return self.p_records

    @property
    @lru_cache(maxsize=1)
    def references_paragraphs(self):
        if self.p_records and self.first_reference and self.last_reference:
            return self.p_records[self.first_reference : self.last_reference + 1]
        return []

    @property
    @lru_cache(maxsize=1)
    def after_references_paragraphs(self):
        if self.p_records and self.last_reference:
            return self.p_records[self.last_reference + 1 :]
        return []

    def _identify_references_range(self):
        for i, item in enumerate(self.p_records):
            if not self.first_reference and item.reference_index:
                self.first_reference = i
            if item.reference_index:
                self.last_reference = i
        logging.info(f"first_reference: {self.first_reference}")
        logging.info(f"last_reference: {self.last_reference}")

    @property
    def parts(self):
        parts = {}
        try:
            parts["before references"] = build_text(self.before_references_paragraphs)
        except Exception as e:
            # logging.exception(e)
            parts["before references"] = get_text(
                get_paragraphs_data(self.before_references_paragraphs)
            )
        try:
            parts["references"] = list(fix_references(self.references_paragraphs))
        except Exception as e:
            # logging.exception(e)
            parts["references"] = list(get_paragraphs_data(self.references_paragraphs))

        try:
            parts["after references"] = build_text(self.after_references_paragraphs)
        except Exception as e:
            # logging.exception(e)
            parts["after references"] = get_text(
                get_paragraphs_data(self.after_references_paragraphs)
            )
        return parts


def get_paragraphs_data(p_records, part_name=None):
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if item.data["text"]:
            # logging.info("Antes:")
            # logging.info(item.data)

            hc = HTMLContent(item.data["text"])
            root = hc.tree.find(".//body/*")
            if part_name:
                root.set("data-part", part_name)

            ref_idx = item.data.get("reference_index")
            if ref_idx:
                root.set("data-ref-index", ref_idx)

            item.data["text"] = hc.content

            # logging.info("Depois:")
            # logging.info(item.data["text"])
            yield item.data


def get_text(items):
    return "".join([item["text"] for item in items or []])


def build_text(p_records):
    document = "".join(fix_paragraphs(p_records))
    if not document:
        return
    hc = HTMLContent(document)    
    hc.fix_asset_paths()
    return hc.content


def fix_paragraphs(p_records):
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if item.data["text"]:
            yield html_fixer.avoid_mismatched_p(item.data["text"])


def fix_references(p_records):
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if item.data["text"]:
            item.data["text"] = html_fixer.avoid_mismatched_p(item.data["text"])               
            yield item.data

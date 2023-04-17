import os
import logging

from scielo_classic_website.utils.files_utils import read_file
from lxml.html import rewrite_links, iterlinks, fromstring, tostring


class HTMLFile:
    """
    """
    def __init__(self, file_path):
        self._html_content = HTMLContent(
            read_file(file_path, encoding="iso-8859-1")
        )

    @property
    def asset_path_fixes(self):
        return self._html_content.asset_path_fixes

    @property
    def old_and_new_links(self):
        return self._html_content.old_and_new_links

    def replace_old_and_new_links(self, file_path=None):
        self._html_content.replace_old_and_new_links()
        if file_path:
            with open(file_path, "w") as fp:
                fp.write(self._html_content.content)
        else:
            return self._html_content.content

    @property
    def body_content(self):
        return self._html_content.body_content


class HTMLContent:
    def __init__(self, content=None):
        self._content = content

    @property
    def body_content(self):
        p = self._content.find("<body")
        if not p:
            return ''
        b = self._content[p:]
        b = b[b.find(">")+1:]
        b = b[:b.find("</body>")]
        return b

    @property
    def content(self):
        return self._content

    @property
    def tree(self):
        if not self._content:
            return
        if not hasattr(self, '_tree') or not self._tree:
            try:
                self._tree = fromstring(self._content)
            except Exception as e:
                self._tree = None
                logging.info(
                    "Unable to get tree {} {}".format(e, self._content))
        return self._tree

    @property
    def asset_path_fixes(self):
        return {
            item['old_link']: item['new_link']
            for item in self.old_and_new_links
        }

    @property
    def old_and_new_links(self):
        if not self.tree:
            return []

        for elem, attr in (("img", "src"), ("a", "href")):
            for node in self.tree.xpath(f"//{elem}"):
                old_link = node.get(attr)
                if not old_link:
                    continue
                if ":" not in old_link:
                    new_link = os.path.realpath(old_link)
                    if os.path.isfile(new_link):
                        for folder in ("htdocs", "bases"):
                            if folder in new_link:
                                new_link = new_link[new_link.find(folder)+len(folder):]
                                logging.info(f"{old_link} {new_link}")
                                yield {"old_link": old_link, "new_link": new_link}
                                break

    def replace_old_and_new_links(self):
        if not self.tree:
            return []
        for elem, attr in (("img", "src"), ("a", "href")):
            for node in self.tree.xpath(f"//{elem}"):
                old_link = node.get(attr)
                if not old_link:
                    continue
                if ":" not in old_link:
                    new_link = os.path.realpath(old_link)
                    if os.path.isfile(new_link):
                        for folder in ("htdocs", "bases"):
                            if folder in new_link:
                                new_link = new_link[new_link.find(folder)+len(folder):]
                                logging.info(f"{old_link} {new_link}")
                                node.set("data-old-link", old_link)
                                node.set(attr, new_link)
                                break
        self._content = tostring(self._tree, encoding="utf-8").decode("utf-8")


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

    def get_paragraphs_data(self, p_records):
        for item in p_records:
            # item.data (dict which keys: text, index, reference_index)
            if item.data['text']:
                html_content = HTMLContent(item.data['text'])
                html_content.replace_old_and_new_links()
                item.data['text'] = html_content.body_content
                yield item.data

    @property
    def before_references_paragraphs(self):
        if not self.p_records:
            return []
        return self.p_records[:self.first_reference]

    @property
    def references_paragraphs(self):
        if not self.p_records:
            return []
        return self.p_records[self.first_reference:self.last_reference+1]

    @property
    def after_references_paragraphs(self):
        if not self.p_records:
            return []
        return self.p_records[self.last_reference+1:]

    def _identify_references_range(self):
        for i, item in enumerate(self.p_records):
            if not self.first_reference and item.reference_index:
                self.first_reference = i
            if item.reference_index:
                self.last_reference = i

    @property
    def parts(self):
        return {
            "before references": list(
                self.get_paragraphs_data(
                    self.before_references_paragraphs)),
            "references": list(
                self.get_paragraphs_data(
                    self.references_paragraphs)),
            "after references": list(
                self.get_paragraphs_data(
                    self.after_references_paragraphs)),
        }


class BodyFromHTMLFile:
    """
    Interface amigável para obter os dados da base isis
    que estão no formato JSON
    """
    def __init__(self, before_references_file_path,
                 reference_texts=None, after_references_file_path=None):
        self.before_references = HTMLFile(before_references_file_path)
        self.after_references = None
        if after_references_file_path:
            self.after_references = HTMLFile(after_references_file_path)
        self.reference_texts = reference_texts or ''

    @property
    def text(self):
        return "".join([
            self.before_references.body_content,
            self.reference_texts,
            self.after_references and self.after_references.body_content or ''
        ])

    @property
    def html(self):
        return f"<html><body>{self.text}</body></html>"

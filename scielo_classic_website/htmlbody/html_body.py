import logging
import os

from lxml.etree import ParseError
from lxml.html import fromstring, html_to_xhtml, iterlinks, rewrite_links, tostring

from scielo_classic_website.htmlbody.html_code_utils import html_safe_decode
from scielo_classic_website.utils.files_utils import read_file


class HTMLFile:
    """ """

    def __init__(self, file_path):
        logging.info(f"HTMLFILE {file_path}")
        self._html_content = HTMLContent(read_file(file_path, encoding="iso-8859-1"))

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


def html2xml(node):
    return (
        # html_safe_decode(
            # tostring(node, method="xml", encoding="utf-8", pretty_print=True).decode(
            tostring(node, method="xml", encoding="utf-8").decode(
                "utf-8"
            )
        # )
    )


class HTMLContent:
    """
    >>> from scielo_classic_website.htmlbody.html_body import HTMLContent
    >>> hc = HTMLContent("<root><p>&nbsp;&ntilde;&#985;<br><hr><img src='x.gif'></root>")
    >>> hc.content
    >>> '<root><p>\xa0ñϙ<br/></p><hr/><img src="x.gif"/></root>'
    """

    def __init__(self, content=None):
        self._content = content
        self.tree = content
        # if content != self.content:
        #     logging.info(content)
        #     logging.info(self.content)

    @property
    def body_content(self):
        if self.tree is None:
            return self._content
        try:
            body = self.tree.find(".//body")
            return html2xml(body)
        except (AttributeError, TypeError):
            return self.content

    @property
    def content(self):
        if self.tree is None:
            return self._content
        return html2xml(self.tree)

    @property
    def tree(self):
        return self._tree

    # def standardize(self, content):
    #     item = content.replace("<", "standardizeBREAK<")
    #     item = item.replace(">", ">standardizeBREAK")
    #     items = item.split("standardizeBREAK")
    #     tags = set((
    #         tag
    #         for tag in items
    #         if tag.startswith("<") and tag.endswith(">")
    #     ))
    #     new_content = content
    #     for tag in tags:
    #         if "/" == tag[1]:
    #             new_content = new_content.replace(tag, "</TAG>")
    #         elif " " in tag:
    #             name = tag[:tag.find(" ")+1]
    #             if name in ("hr", "br", "img"):
    #                 new_tag = f'<TAG NAME="{name}" '
    #             else:
    #                 new_tag = f'<TAG NAME="{name}" '
    #             new_content = new_content.replace(tag, new_tag)
    #         else:
    #             name = tag[1:-1].lower()
    #             if name in ("hr", "br", "img"):
    #                 new_tag = f'<TAG NAME="{name}"/>'
    #             else:
    #                 new_tag = f'<TAG NAME="{name}">'
    #             new_content = new_content.replace(tag, new_tag)
    #     return new_content

    @tree.setter
    def tree(self, content):
        self._tree = None
        if not content.strip():
            content = "<span></span>"
        try:
            self._tree = fromstring(content)
            return
        except Exception as e:
            pass
            # logging.exception(f"Error 1 {type(e)} {e} {content}")

        # try:
        #     html_safe_content = html_safe_decode(content)
        #     self._tree = fromstring(html_safe_content)
        #     return
        # except Exception as e:
        #     pass
        #     # logging.exception(f"Error 2 {type(e)} {e} {content}")

        try:
            alt_content = (
                f'<span data-bad-format="yes"><!-- {content} --></span>'
            )
            self._tree = fromstring(alt_content)
            return
        except Exception as e:
            pass
            # logging.exception(f"Error 3 {type(e)} {e} {content}")

        logging.error(f"HTMLContent {content}")

    @property
    def asset_path_fixes(self):
        return {item["old_link"]: item["new_link"] for item in self.old_and_new_links}

    @property
    def old_and_new_links(self):
        if self.tree is None:
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
                                new_link = new_link[
                                    new_link.find(folder) + len(folder) :
                                ]
                                logging.info({"old_link": old_link, "new_link": new_link})
                                yield {"old_link": old_link, "new_link": new_link}
                                break

    def replace_old_and_new_links(self):
        if self.tree is None:
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
                                new_link = new_link[
                                    new_link.find(folder) + len(folder) :
                                ]
                                logging.info(f"old {old_link} => new {new_link}")
                                node.set("data-old-link", old_link)
                                node.set(attr, new_link)
                                break


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

    def get_paragraphs_data(self, p_records, part_name=None):
        for item in p_records:
            # item.data (dict which keys: text, index, reference_index)
            if item.data["text"]:
                # logging.info("Antes:")
                # logging.info(item.data)

                hc = HTMLContent(item.data["text"])
                root = hc.tree.find(".")
                if part_name:
                    root.set("data-part", part_name)

                ref_idx = item.data.get("reference_index")
                if ref_idx:
                    root.set("data-ref-index", ref_idx)

                hc.replace_old_and_new_links()
                item.data["text"] = hc.content

                # logging.info("Depois:")
                # logging.info(item.data["text"])
                yield item.data

    @property
    def before_references_paragraphs(self):
        if self.p_records and self.first_reference:
            return self.p_records[: self.first_reference]
        return self.p_records

    @property
    def references_paragraphs(self):
        if self.p_records and self.first_reference and self.last_reference:
            return self.p_records[self.first_reference : self.last_reference + 1]
        return []

    @property
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
        return {
            "before references": list(
                self.get_paragraphs_data(self.before_references_paragraphs)
            ),
            "references": list(self.get_paragraphs_data(self.references_paragraphs)),
            "after references": list(
                self.get_paragraphs_data(self.after_references_paragraphs)
            ),
        }


class BodyFromHTMLFile:
    """
    Interface amigável para obter os dados da base isis
    que estão no formato JSON
    """

    def __init__(
        self,
        before_references_file_path,
        reference_texts=None,
        after_references_file_path=None,
    ):
        self.before_references = HTMLFile(before_references_file_path)
        self.after_references = None
        if after_references_file_path:
            self.after_references = HTMLFile(after_references_file_path)
        self.reference_texts = reference_texts or ""

    @property
    def text(self):
        return "".join(
            [
                self.before_references.body_content,
                self.reference_texts,
                self.after_references and self.after_references.body_content or "",
            ]
        )

    @property
    def html(self):
        return f"<html><body>{self.text}</body></html>"

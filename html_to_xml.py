"""
Converte HTML em XML.
"""
from lxml import etree

from fixtures import MAIN_HTML_PARAGRAPHS, TRANSLATED_HTML_BY_LANG
from scielo_classic_website.spsxml.sps_xml_body_pipes import convert_html_to_xml


def get_tree(xml_str):
    return etree.fromstring(xml_str)


def tree_tostring_decode(_str):
    return etree.tostring(_str, encoding="utf-8").decode("utf-8")


def pretty_print(_str):
    return etree.tostring(get_tree(_str), encoding="utf-8", pretty_print=True).decode(
        "utf-8"
    )


class IncompleteDocument:
    def __init__(self):
        self.main_html_paragraphs = MAIN_HTML_PARAGRAPHS
        self.translated_html_by_lang = TRANSLATED_HTML_BY_LANG


def save_file(filename, result):
    # tree = etree.ElementTree(result)
    with open(filename, "w") as f:
        f.write(pretty_print(result))


def main():
    document = IncompleteDocument()

    convert_html_to_xml(document)

    result = document.xml_body_and_back

    for i, item in enumerate(result):
        print(pretty_print(item))
        save_file(f"/tmp/output_{i}.xml", item)


if __name__ == "__main__":
    main()

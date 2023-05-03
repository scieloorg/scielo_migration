from io import StringIO

from lxml import etree as ET

STYLES = (
    ("<u ", '<span name="style_underline" '),
    ("<strong ", '<span name="style_bold" '),
    ("<em ", '<span name="style_bold" '),
    ("<b ", '<span name="style_bold" '),
    ("<i ", '<span name="style_italic" '),
    ("<sup ", '<span name="style_sup" '),
    ("<sub ", '<span name="style_sub" '),
    ("<u>", '<span name="style_underline" '),
    ("<strong>", '<span name="style_bold">'),
    ("<em>", '<span name="style_bold">'),
    ("<b>", '<span name="style_bold">'),
    ("<i>", '<span name="style_italic">'),
    ("<sup>", '<span name="style_sup">'),
    ("<sub>", '<span name="style_sub">'),
    ("</u>", "</span>"),
    ("</em>", "</span>"),
    ("</strong>", "</span>"),
    ("</b>", "</span>"),
    ("</i>", "</span>"),
    ("</sub>", "</span>"),
    ("</sup>", "</span>"),
)


def get_html_tree(html_str):
    parser = ET.HTMLParser()

    for old, new in STYLES:
        html_str = html_str.replace(old, new)
        html_str = html_str.replace(old.upper(), new)
    return ET.parse(StringIO(html_str), parser)


def get_mixed_citation_node(reference_html_paragraph):
    html_tree = get_html_tree(reference_html_paragraph)
    p = html_tree.find(".//body/p")
    if p is not None:
        p.tag = "mixed-citation"
    return p

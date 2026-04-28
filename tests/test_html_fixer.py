from unittest import TestCase

from lxml import etree as ET
from lxml import html as lxml_html

from scielo_classic_website.htmlbody.html_fixer import (
    get_fixed_html,
    load_html,
    remove_invalid_namespace_attributes,
    remove_invalid_xml_comments,
)


class TestRemoveInvalidXmlComments(TestCase):
    def test_removes_clipboard_artifact_endF(self):
        html = "<p>text</p><!--EndF>><!--EndFragment--><p>more</p>"
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, "<p>text</p><p>more</p>")

    def test_removes_clipboard_artifact_endFrag(self):
        html = "<p>text</p><!--EndFrag>><!--EndFragment--><p>more</p>"
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, "<p>text</p><p>more</p>")

    def test_preserves_valid_comment(self):
        html = "<p>text</p><!-- valid comment --><p>more</p>"
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, html)

    def test_returns_none_for_none(self):
        self.assertIsNone(remove_invalid_xml_comments(None))

    def test_returns_empty_for_empty(self):
        self.assertEqual(remove_invalid_xml_comments(""), "")

    def test_no_comments(self):
        html = "<p>text</p><p>more</p>"
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, html)

    def test_sanitized_output_is_valid_xml(self):
        html = "<root><p>text</p><!--EndF>><!--EndFragment--><p>more</p></root>"
        sanitized = remove_invalid_xml_comments(html)
        tree = ET.fromstring(sanitized)
        self.assertIsNotNone(tree)
        self.assertEqual(tree.tag, "root")

    def test_multiple_invalid_comments(self):
        html = (
            "<p>intro</p>"
            "<!--EndF>><!--EndFragment-->"
            "<p>middle</p>"
            "<!--EndFrag>><!--EndFragment-->"
            "<p>end</p>"
        )
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, "<p>intro</p><p>middle</p><p>end</p>")

    def test_mixed_valid_and_invalid_comments(self):
        html = (
            "<!-- valid -->"
            "<p>text</p>"
            "<!--EndF>><!--EndFragment-->"
            "<p>more</p>"
        )
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, "<!-- valid --><p>text</p><p>more</p>")

    def test_preserves_startfragment_endfragment_pair(self):
        html = "<p>text</p><!--StartFragment--><!--EndFragment-->"
        result = remove_invalid_xml_comments(html)
        # These are valid XML comments individually (no -- inside),
        # so they should be preserved
        self.assertEqual(result, html)

    def test_multiline_invalid_comment(self):
        html = "<p>text</p><!--EndF>>\n<!--EndFragment--><p>more</p>"
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, "<p>text</p><p>more</p>")


class TestRemoveInvalidNamespaceAttributes(TestCase):
    def test_removes_undefined_namespace_attribute(self):
        tree = lxml_html.fromstring(
            '<html><body><a mailto:dade="x" href="y">link</a></body></html>'
        )
        remove_invalid_namespace_attributes(tree)
        a = tree.find(".//a")
        self.assertNotIn("mailto:dade", a.attrib)
        self.assertEqual(a.get("href"), "y")

    def test_serialized_tree_is_valid_xml(self):
        tree = lxml_html.fromstring(
            '<html><body><a mailto:dade="x" href="y">link</a></body></html>'
        )
        remove_invalid_namespace_attributes(tree)
        serialized = ET.tostring(tree, method="xml").decode("utf-8")
        # Re-parsing as XML must not raise XMLSyntaxError
        ET.fromstring(serialized)

    def test_preserves_xml_and_xlink_prefixes(self):
        tree = lxml_html.fromstring(
            '<html><body>'
            '<a xml:lang="pt" xlink:href="x" mailto:foo="y">link</a>'
            '</body></html>'
        )
        remove_invalid_namespace_attributes(tree)
        a = tree.find(".//a")
        self.assertEqual(a.get("xml:lang"), "pt")
        self.assertEqual(a.get("xlink:href"), "x")
        self.assertNotIn("mailto:foo", a.attrib)

    def test_preserves_attributes_without_colon(self):
        tree = lxml_html.fromstring(
            '<html><body><p id="x" class="y">text</p></body></html>'
        )
        remove_invalid_namespace_attributes(tree)
        p = tree.find(".//p")
        self.assertEqual(p.get("id"), "x")
        self.assertEqual(p.get("class"), "y")

    def test_handles_none_tree(self):
        self.assertIsNone(remove_invalid_namespace_attributes(None))

    def test_load_html_strips_invalid_namespace_attributes(self):
        tree = load_html('<p>foo <a mailto:dade="z" href="y">link</a> bar</p>')
        a = tree.find(".//a")
        self.assertNotIn("mailto:dade", a.attrib)
        # Tree must serialize to valid XML
        serialized = ET.tostring(tree, method="xml").decode("utf-8")
        ET.fromstring(serialized)

    def test_get_fixed_html_output_is_valid_xml(self):
        # Attribute value contains '>' so the regex-based
        # ``remove_namespaces_from_content`` step (used inside ``fix()``)
        # cannot reliably strip the bad attribute. The tree-level cleanup
        # must still produce XML that re-parses without errors.
        content = '<p>Hello <a mailto:dade="a>b" href="x">world</a></p>'
        result = get_fixed_html(content)
        wrapped = f"<root>{result}</root>"
        ET.fromstring(wrapped)

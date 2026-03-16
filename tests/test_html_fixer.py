from unittest import TestCase

from lxml import etree as ET

from scielo_classic_website.htmlbody.html_fixer import remove_invalid_xml_comments


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

    def test_removes_startfragment_endfragment_pair(self):
        html = "<p>text</p><!--StartFragment--><!--EndFragment-->"
        result = remove_invalid_xml_comments(html)
        # These are valid XML comments individually (no -- inside),
        # so they should be preserved
        self.assertEqual(result, html)

    def test_multiline_invalid_comment(self):
        html = "<p>text</p><!--EndF>>\n<!--EndFragment--><p>more</p>"
        result = remove_invalid_xml_comments(html)
        self.assertEqual(result, "<p>text</p><p>more</p>")

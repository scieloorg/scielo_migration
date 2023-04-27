from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.sps_xml_body_pipes import OlPipe


def get_tree(xml_str):
    return etree.fromstring(xml_str)


class TestOlPipe(TestCase):

    def test_ol_pipe(self):
        raw = None
        xml = get_tree("<root><body><ol>Um</ol></body></root>")
        expected = (
            '<root>'
            '<body>'
            '<list list-type="order">'
            'Um'
            '</list>'
            '</body>'
            '</root>'
        )
        data = (raw, xml)
        _raw, _xml = OlPipe().transform(data)
        result = etree.tostring(_xml, encoding='utf-8').decode('utf-8')
        self.assertEqual(1, len(_xml.xpath(".//list[@list-type='order']")))
        self.assertEqual(expected, result)

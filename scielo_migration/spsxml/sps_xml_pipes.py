
import plumber
from lxml import etree as ET


def get_xml_rsps(document):
    """
    Obtém XML

    Parameters
    ----------
    document: dict
    """
    return _process(document)


def _process(document):
    """
    Aplica as transformações

    Parameters
    ----------
    document: dict
    """
    ppl = plumber.Pipeline(
            SetupArticlePipe(),
            XMLClosePipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


class SetupArticlePipe(plumber.Pipe):
    """
    Create `<article specific-use="sps-1.4" dtd-version="1.0"/>`
    """
    def transform(self, data):

        nsmap = {
            'xml': 'http://www.w3.org/XML/1998/namespace',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        xml = ET.Element('article', nsmap=nsmap)
        xml.set('specific-use', 'sps-1.4')
        xml.set('dtd-version', '1.0')
        return data, xml


class XMLClosePipe(plumber.Pipe):
    """
    Insere `<!DOCTYPE...`
    """
    def transform(self, data):
        raw, xml = data

        data = ET.tostring(
            xml,
            encoding="utf-8",
            method="xml",
            doctype=(
                '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) '
                'Journal Publishing DTD v1.0 20120330//EN" '
                '"JATS-journalpublishing1.dtd">')
            )
        return data

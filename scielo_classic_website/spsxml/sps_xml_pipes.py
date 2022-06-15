
import plumber
from lxml import etree as ET

from scielo_classic_website.spsxml.sps_xml_attributes import (
    ARTICLE_TYPES,
    COUNTRY_ITEMS,
)

from scielo_migration.spsxml.sps_xml_article_meta import (
    XMLArticleMetaSciELOArticleIdPipe,
    XMLArticleMetaArticleIdDOIPipe,
    XMLArticleMetaArticleCategoriesPipe,
    XMLArticleMetaTitleGroupPipe,
    XMLArticleMetaTranslatedTitleGroupPipe,
    XMLArticleMetaContribGroupPipe,
    XMLArticleMetaAffiliationPipe,
    XMLArticleMetaPublicationDatesPipe,
    XMLArticleMetaIssueInfoPipe,
    XMLArticleMetaElocationInfoPipe,
    XMLArticleMetaPagesInfoPipe,
    XMLArticleMetaHistoryPipe,
    # XMLArticleMetaPermissionPipe,
    # XMLArticleMetaSelfUriPipe,
    # XMLArticleMetaAbstractsPipe,
    # XMLArticleMetaKeywordsPipe,
    # XMLArticleMetaCountsPipe,
    # XMLBodyPipe,
    # XMLArticleMetaCitationsPipe,
    # XMLSubArticlePipe,
)


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
            XMLArticlePipe(),
            XMLFrontPipe(),
            XMLJournalMetaJournalIdPipe(),
            XMLJournalMetaJournalTitleGroupPipe(),
            XMLJournalMetaISSNPipe(),
            XMLJournalMetaPublisherPipe(),
            XMLArticleMetaSciELOArticleIdPipe(),
            XMLArticleMetaArticleIdDOIPipe(),
            XMLArticleMetaArticleCategoriesPipe(),
            XMLArticleMetaTitleGroupPipe(),
            XMLArticleMetaTranslatedTitleGroupPipe(),
            XMLArticleMetaContribGroupPipe(),
            XMLArticleMetaAffiliationPipe(),
            XMLArticleMetaPublicationDatesPipe(),
            XMLArticleMetaIssueInfoPipe(),
            XMLArticleMetaElocationInfoPipe(),
            XMLArticleMetaPagesInfoPipe(),
            XMLArticleMetaHistoryPipe(),
            # XMLArticleMetaPermissionPipe(),
            # XMLArticleMetaSelfUriPipe(),
            # XMLArticleMetaAbstractsPipe(),
            # XMLArticleMetaKeywordsPipe(),
            # XMLArticleMetaCountsPipe(),
            # XMLBodyPipe(),
            # XMLArticleMetaCitationsPipe(),
            # XMLSubArticlePipe(),
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


class XMLArticlePipe(plumber.Pipe):
    def precond(data):
        raw, xml = data
        try:
            if not raw.document_type or not raw.original_language:
                raise plumber.UnmetPrecondition()
        except AttributeError:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        document_type = ARTICLE_TYPES.get(raw.document_type)
        xml.set('{http://www.w3.org/XML/1998/namespace}lang', raw.original_language)
        xml.set('article-type', document_type)

        return data


class XMLFrontPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        xml.append(ET.Element('front'))

        front = xml.find('front')
        front.append(ET.Element('journal-meta'))
        front.append(ET.Element('article-meta'))

        return data


class XMLJournalMetaJournalIdPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        journal_meta = xml.find('./front/journal-meta')

        journalid = ET.Element('journal-id')
        journalid.text = raw.journal.acronym
        journalid.set('journal-id-type', 'publisher-id')

        journal_meta.append(journalid)

        return data


class XMLJournalMetaJournalTitleGroupPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        journaltitle = ET.Element('journal-title')
        journaltitle.text = raw.journal.title

        journalabbrevtitle = ET.Element('abbrev-journal-title')
        journalabbrevtitle.text = raw.journal.abbreviated_title
        journalabbrevtitle.set('abbrev-type', 'publisher')

        journaltitlegroup = ET.Element('journal-title-group')
        journaltitlegroup.append(journaltitle)
        journaltitlegroup.append(journalabbrevtitle)

        xml.find('./front/journal-meta').append(journaltitlegroup)

        return data


class XMLJournalMetaISSNPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        if raw.journal.print_issn:
            pissn = ET.Element('issn')
            pissn.text = raw.journal.print_issn
            pissn.set('pub-type', 'ppub')
            xml.find('./front/journal-meta').append(pissn)

        if raw.journal.electronic_issn:
            eissn = ET.Element('issn')
            eissn.text = raw.journal.electronic_issn
            eissn.set('pub-type', 'epub')
            xml.find('./front/journal-meta').append(eissn)

        return data


class XMLJournalMetaPublisherPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        publisher = ET.Element('publisher')

        publishername = ET.Element('publisher-name')
        publishername.text = u'; '.join(raw.journal.publisher_name or [])
        publisher.append(publishername)

        if raw.journal.publisher_country:
            countrycode = raw.journal.publisher_country
            countryname = COUNTRY_ITEMS.name(countrycode)
            publishercountry = countryname or countrycode

        publisherloc = [
            raw.journal.publisher_city or u'',
            raw.journal.publisher_state or u'',
            publishercountry
        ]

        if raw.journal.publisher_country:
            publishercountry = ET.Element('publisher-loc')
            publishercountry.text = ', '.join(publisherloc)
            publisher.append(publishercountry)

        xml.find('./front/journal-meta').append(publisher)

        return data

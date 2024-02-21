import logging
from copy import deepcopy

import plumber
from lxml import etree as ET

from scielo_classic_website.spsxml.sps_xml_article_meta import (
    XMLArticleMetaAbstractsPipe,
    XMLArticleMetaAffiliationPipe,
    XMLArticleMetaArticleCategoriesPipe,
    XMLArticleMetaArticleIdDOIPipe,
    XMLArticleMetaContribGroupPipe,
    XMLArticleMetaCountsPipe,
    XMLArticleMetaElocationInfoPipe,
    XMLArticleMetaHistoryPipe,
    XMLArticleMetaIssueInfoPipe,
    XMLArticleMetaKeywordsPipe,
    XMLArticleMetaPagesInfoPipe,
    XMLArticleMetaPermissionPipe,
    XMLArticleMetaPublicationDatesPipe,
    XMLArticleMetaSciELOArticleIdPipe,
    XMLArticleMetaSelfUriPipe,
    XMLArticleMetaTitleGroupPipe,
    XMLArticleMetaTranslatedTitleGroupPipe,
    XMLNormalizeSpacePipe,
)
from scielo_classic_website.spsxml.sps_xml_attributes import (
    get_article_type,
    country_name,
)
from scielo_classic_website.spsxml.sps_xml_refs import XMLArticleMetaCitationsPipe


def get_xml_rsps(document):
    """
    Obtém XML

    Parameters
    ----------
    document: dict
    """
    return _process(document)


def _process(document, data):
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
        XMLArticleMetaPermissionPipe(),
        XMLArticleMetaSelfUriPipe(),
        XMLArticleMetaAbstractsPipe(),
        XMLArticleMetaKeywordsPipe(),
        XMLBodyPipe(),
        XMLBackPipe(),
        XMLArticleMetaCitationsPipe(),
        XMLSubArticlePipe(),
        XMLArticleMetaCountsPipe(),
        XMLNormalizeSpacePipe(),
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
            "xml": "http://www.w3.org/XML/1998/namespace",
            "xlink": "http://www.w3.org/1999/xlink",
        }

        xml = ET.Element("article", nsmap=nsmap)

        try:
            xml.set("specific-use", data.params_for_xml_creation["specific-use"])
        except (KeyError, AttributeError):
            xml.set("specific-use", "sps-1.10")
        try:
            xml.set("dtd-version", data.params_for_xml_creation["dtd-version"])
        except (KeyError, AttributeError):
            xml.set("dtd-version", "1.3")
        return data, xml


class XMLClosePipe(plumber.Pipe):
    """
    Insere `<!DOCTYPE...`
    """

    def transform(self, data):
        raw, xml = data

        try:
            doctype = raw.params_for_xml_creation["doctype"]
        except (KeyError, AttributeError):
            doctype = (
                '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) '
                'Journal Publishing DTD v1.3 20210610//EN" '
                '"JATS-journalpublishing1-3.dtd">'
            )

        data = ET.tostring(
            xml,
            encoding="utf-8",
            method="xml",
            xml_declaration=True,
            pretty_print=True,
            doctype=doctype,
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

        document_type = get_article_type(raw.document_type)
        xml.set("{http://www.w3.org/XML/1998/namespace}lang", raw.original_language)
        xml.set("article-type", document_type or raw.document_type)

        return data


class XMLFrontPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        xml.append(ET.Element("front"))

        front = xml.find("front")
        front.append(ET.Element("journal-meta"))
        front.append(ET.Element("article-meta"))

        return data


class XMLJournalMetaJournalIdPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        journal_meta = xml.find("./front/journal-meta")

        journalid = ET.Element("journal-id")
        journalid.text = raw.journal.acronym
        journalid.set("journal-id-type", "publisher-id")

        journal_meta.append(journalid)

        return data


class XMLJournalMetaJournalTitleGroupPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        journaltitle = ET.Element("journal-title")
        journaltitle.text = raw.journal.title

        journalabbrevtitle = ET.Element("abbrev-journal-title")
        journalabbrevtitle.text = raw.journal.abbreviated_title
        journalabbrevtitle.set("abbrev-type", "publisher")

        journaltitlegroup = ET.Element("journal-title-group")
        journaltitlegroup.append(journaltitle)
        journaltitlegroup.append(journalabbrevtitle)

        xml.find("./front/journal-meta").append(journaltitlegroup)

        return data


class XMLJournalMetaISSNPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        if raw.journal.print_issn:
            pissn = ET.Element("issn")
            pissn.text = raw.journal.print_issn
            pissn.set("pub-type", "ppub")
            xml.find("./front/journal-meta").append(pissn)

        if raw.journal.electronic_issn:
            eissn = ET.Element("issn")
            eissn.text = raw.journal.electronic_issn
            eissn.set("pub-type", "epub")
            xml.find("./front/journal-meta").append(eissn)

        return data


class XMLJournalMetaPublisherPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        publisher = ET.Element("publisher")

        publishername = ET.Element("publisher-name")
        publishername.text = "; ".join(raw.journal.publisher_name or [])
        publisher.append(publishername)

        logging.debug("XMLJournalMetaPublisherPipe")
        if raw.journal.publisher_country:
            countrycode = raw.journal.publisher_country
            countryname = country_name(countrycode)
            publishercountry = countryname or countrycode
        logging.debug("---XMLJournalMetaPublisherPipe")

        publisherloc = [
            raw.journal.publisher_city or "",
            raw.journal.publisher_state or "",
            publishercountry,
        ]

        if raw.journal.publisher_country:
            publishercountry = ET.Element("publisher-loc")
            publishercountry.text = ", ".join(publisherloc)
            publisher.append(publishercountry)

        xml.find("./front/journal-meta").append(publisher)

        return data


class XMLBodyPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.xml_body:
            logging.exception("XMLBodyPipe not found raw.xml_body")
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        converted_html_body = ET.fromstring(raw.xml_body)
        body = deepcopy(converted_html_body.find(".//body"))
        body.set("specific-use", "quirks-mode")
        xml.append(body)
        return data


class XMLBackPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.xml_body:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        converted_html_body = ET.fromstring(raw.xml_body)
        back = converted_html_body.find(".//back")
        if back is not None:
            xml.append(deepcopy(back))
        return data


class XMLSubArticlePipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.xml_body:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        converted_html_body = ET.fromstring(raw.xml_body)
        for subart in converted_html_body.findall(".//sub-article"):
            subarticle = deepcopy(subart)
            xml.append(subarticle)

            language = subarticle.get("{http://www.w3.org/XML/1998/namespace}lang")

            # FRONT STUB
            frontstub = ET.Element("front-stub")

            # ARTICLE CATEGORY
            logging.info("raw %s" % type(raw))
            if raw.section:
                articlecategories = ET.Element("article-categories")
                subjectgroup = ET.Element("subj-group")
                subjectgroup.set("subj-group-type", "heading")
                sbj = ET.Element("subject")
                sbj.text = raw.get_section(language)
                subjectgroup.append(sbj)
                articlecategories.append(subjectgroup)
                frontstub.append(articlecategories)

            # ARTICLE TITLE
            if raw.translated_titles:
                titlegroup = ET.Element("title-group")
                articletitle = ET.Element("article-title")
                articletitle.set("{http://www.w3.org/XML/1998/namespace}lang", language)
                title = raw.get_article_title(language)
                if "&" in title:
                    articletitle.text = ET.CDATA(title)
                else:
                    articletitle.text = title
                titlegroup.append(articletitle)
                frontstub.append(titlegroup)

            # ABSTRACT
            if raw.translated_abstracts:
                p = ET.Element("p")
                text = raw.get_abstract(language)
                if "&" in text:
                    p.text = ET.CDATA(text)
                else:
                    p.text = text
                abstract = ET.Element("abstract")
                abstract.set("{http://www.w3.org/XML/1998/namespace}lang", language)
                abstract.append(p)
                frontstub.append(abstract)

            # KEYWORDS
            keywords_group = raw.get_keywords_group(language)
            if keywords_group:
                kwd_group = ET.Element("kwd-group")
                kwd_group.set("{http://www.w3.org/XML/1998/namespace}lang", language)
                for item in keywords_group:
                    kwd = ET.Element("kwd")
                    kwd.text = ET.CDATA(item) if "&" in item else item
                    kwd_group.append(kwd)
                frontstub.append(kwd_group)
            subarticle.append(frontstub)
        return data

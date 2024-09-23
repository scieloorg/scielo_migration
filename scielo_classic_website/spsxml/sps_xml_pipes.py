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
    create_node_with_fixed_html_text,
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
        XMLArticleMetaPermissionPipe(),
        XMLArticleMetaSelfUriPipe(),
        XMLArticleMetaAbstractsPipe(),
        XMLArticleMetaKeywordsPipe(),
        XMLBodyPipe(),
        XMLBackPipe(),
        XMLArticleMetaCitationsPipe(),
        XMLSubArticlePipe(),
        XMLStylePipe(),
        XMLArticleMetaCountsPipe(),
        XMLNormalizeSpacePipe(),
        XMLDeleteRepeatedElementWithId(),
        XMLFontFaceSymbolPipe(),
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
        except Exception as e:
            logging.exception(e)
            xml.set("specific-use", "sps-1.10")
        try:
            xml.set("dtd-version", data.params_for_xml_creation["dtd-version"])
        except (KeyError, AttributeError):
            xml.set("dtd-version", "1.3")
        except Exception as e:
            logging.exception(e)
            xml.set("dtd-version", "1.3")
        return data, xml


class XMLDeleteRepeatedElementWithId(plumber.Pipe):
    def fix_id_and_rid(self, root):
        subarticle_id = root.get("id")
        items = []
        for node in root.xpath(".//*[@id]"):
            _id = node.get("id")
            item = (node.tag, _id)
            if item in items:
                elem = ET.Element("EMPTYTAGTOSTRIP")
                node.addnext(elem)
                parent = node.getparent()
                parent.remove(node)
            else:
                items.append(item)
                if subarticle_id:
                    new_id = f'{subarticle_id}{_id}'
                else:
                    new_id = _id
                node.set("id", new_id)
                for xref in root.xpath(f".//xref[@rid='{_id}']"):
                    xref.set("rid", new_id)

    def transform(self, data):
        raw, xml = data

        for subarticle in xml.xpath("sub-article[@article-type='translation']"):
            self.fix_id_and_rid(subarticle)
        self.fix_id_and_rid(xml.find("."))
        ET.strip_tags(xml, "EMPTYTAGTOSTRIP")
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
        except Exception as e:
            logging.exception(e)
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
                sbj.text = raw.get_section_title(language)
                subjectgroup.append(sbj)
                articlecategories.append(subjectgroup)
                frontstub.append(articlecategories)

            # ARTICLE TITLE
            if raw.translated_titles:
                titlegroup = ET.Element("title-group")
                title = raw.get_article_title(language)
                articletitle = create_node_with_fixed_html_text("article-title", title)
                articletitle.set("{http://www.w3.org/XML/1998/namespace}lang", language)
                titlegroup.append(articletitle)
                frontstub.append(titlegroup)

            # ABSTRACT
            if raw.translated_abstracts:
                text = raw.get_abstract(language)
                abstract = create_node_with_fixed_html_text("p", text)
                abstract.set("{http://www.w3.org/XML/1998/namespace}lang", language)
                abstract.append(p)
                frontstub.append(abstract)

            # KEYWORDS
            keywords_group = raw.get_keywords_group(language)
            if keywords_group:
                kwd_group = ET.Element("kwd-group")
                kwd_group.set("{http://www.w3.org/XML/1998/namespace}lang", language)
                for item in keywords_group:
                    kwd_group.append(create_node_with_fixed_html_text("kwd", item))
                frontstub.append(kwd_group)
            subarticle.append(frontstub)
        return data


class XMLStylePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        for style in ("bold", "italic", "sup", "sub", "underline"):
            xpath = f".//span[@name='style_{style}']"
            for node in xml.xpath(xpath):
                node.tag = style
                node.attrib.pop("name")
        return data


class XMLFontFaceSymbolPipe(plumber.Pipe):
    # https://www.alanwood.net/demos/symbol.html
    FONTFACESYMBOL = {
        '!': {"char": "!", "name": "Exclamation mark"},
        '#': {"char": "#", "name": "Number sign"},
        '%': {"char": "%", "name": "Percent sign"},
        '&': {"char": "&", "name": "Ampersand"},
        '(': {"char": "(", "name": "Left parenthesis"},
        ')': {"char": ")", "name": "Right parenthesis"},
        '+': {"char": "+", "name": "Plus sign"},
        ',': {"char": ",", "name": "Comma"},
        '.': {"char": ".", "name": "Full stop"},
        '/': {"char": "/", "name": "Solidus"},
        '0': {"char": "0", "name": "Digit zero"},
        '1': {"char": "1", "name": "Digit one"},
        '2': {"char": "2", "name": "Digit two"},
        '3': {"char": "3", "name": "Digit three"},
        '4': {"char": "4", "name": "Digit four"},
        '5': {"char": "5", "name": "Digit five"},
        '6': {"char": "6", "name": "Digit six"},
        '7': {"char": "7", "name": "Digit seven"},
        '8': {"char": "8", "name": "Digit eight"},
        '9': {"char": "9", "name": "Digit nine"},
        ':': {"char": ":", "name": "Colon"},
        ';': {"char": ";", "name": "Semicolon"},
        '<': {"char": "<", "name": "Less-than sign"},
        '=': {"char": "=", "name": "Equals sign"},
        '>': {"char": ">", "name": "Greater-than sign"},
        '?': {"char": "?", "name": "Question mark"},
        '[': {"char": "[", "name": "Left square bracket"},
        ']': {"char": "]", "name": "Right square bracket"},
        '_': {"char": "_", "name": "Low line"},
        '{': {"char": "{", "name": "Left curly bracket"},
        '|': {"char": "|", "name": "Vertical line"},
        '}': {"char": "}", "name": "Right curly bracket"},
        'A': {"char": "Α", "name": "Greek capital letter alpha"},
        'B': {"char": "Β", "name": "Greek capital letter beta"},
        'G': {"char": "Γ", "name": "Greek capital letter gamma"},
        'D': {"char": "Δ", "name": "Greek capital letter delta"},
        'E': {"char": "Ε", "name": "Greek capital letter epsilon"},
        'Z': {"char": "Ζ", "name": "Greek capital letter zeta"},
        'H': {"char": "Η", "name": "Greek capital letter eta"},
        'Q': {"char": "Θ", "name": "Greek capital letter theta"},
        'I': {"char": "Ι", "name": "Greek capital letter iota"},
        'K': {"char": "Κ", "name": "Greek capital letter kappa"},
        'L': {"char": "Λ", "name": "Greek capital letter lamda"},
        'M': {"char": "Μ", "name": "Greek capital letter mu"},
        'N': {"char": "Ν", "name": "Greek capital letter nu"},
        'X': {"char": "Ξ", "name": "Greek capital letter xi"},
        'O': {"char": "Ο", "name": "Greek capital letter omicron"},
        'P': {"char": "Π", "name": "Greek capital letter pi"},
        'R': {"char": "Ρ", "name": "Greek capital letter rho"},
        'S': {"char": "Σ", "name": "Greek capital letter sigma"},
        'T': {"char": "Τ", "name": "Greek capital letter tau"},
        'U': {"char": "Υ", "name": "Greek capital letter upsilon"},
        'F': {"char": "Φ", "name": "Greek capital letter phi"},
        'C': {"char": "Χ", "name": "Greek capital letter chi"},
        'Y': {"char": "Ψ", "name": "Greek capital letter psi"},
        'W': {"char": "Ω", "name": "Greek capital letter omega"},
        'a': {"char": "α", "name": "Greek small letter alpha"},
        'b': {"char": "β", "name": "Greek small letter beta"},
        'g': {"char": "γ", "name": "Greek small letter gamma"},
        'd': {"char": "δ", "name": "Greek small letter delta"},
        'e': {"char": "ε", "name": "Greek small letter epsilon"},
        'z': {"char": "ζ", "name": "Greek small letter zeta"},
        'h': {"char": "η", "name": "Greek small letter eta"},
        'q': {"char": "θ", "name": "Greek small letter theta"},
        'i': {"char": "ι", "name": "Greek small letter iota"},
        'k': {"char": "κ", "name": "Greek small letter kappa"},
        'l': {"char": "λ", "name": "Greek small letter lamda"},
        'm': {"char": "μ", "name": "Greek small letter mu"},
        'n': {"char": "ν", "name": "Greek small letter nu"},
        'x': {"char": "ξ", "name": "Greek small letter xi"},
        'o': {"char": "ο", "name": "Greek small letter omicron"},
        'p': {"char": "π", "name": "Greek small letter pi"},
        'r': {"char": "ρ", "name": "Greek small letter rho"},
        'V': {"char": "ς", "name": "Greek small letter final sigma"},
        's': {"char": "σ", "name": "Greek small letter sigma"},
        't': {"char": "τ", "name": "Greek small letter tau"},
        'u': {"char": "υ", "name": "Greek small letter upsilon"},
        'f': {"char": "φ", "name": "Greek small letter phi"},
        'c': {"char": "χ", "name": "Greek small letter chi"},
        'y': {"char": "ψ", "name": "Greek small letter psi"},
        'w': {"char": "ω", "name": "Greek small letter omega"},
        'J': {"char": "ϑ", "name": "Greek theta symbol"},
        'j': {"char": "ϕ", "name": "Greek phi symbol"},
        'v': {"char": "ϖ", "name": "Greek pi symbol"},
        '¡': {"char": "ϒ", "name": "Greek upsilon with hook symbol"},
        '¢': {"char": "′", "name": "Prime"},
        '¤': {"char": "⁄", "name": "Fraction slash"},
        '²': {"char": "″", "name": "Double prime"},
        '¼': {"char": "…", "name": "Horizontal ellipsis"},        
        'À': {"char": "ℵ", "name": "Alef symbol"},
        'Á': {"char": "ℑ", "name": "Black-letter capital I"},
        'Â': {"char": "ℜ", "name": "Black-letter capital R"},
        'Ã': {"char": "℘", "name": "Script capital P"},
        'Ô': {"char": "™", "name": "Trade mark sign (serif)"},
        'ä': {"char": "™", "name": "Trade mark sign (sans-serif)"},
        'ð': {"char": "€", "name": "Euro sign"},
        '«': {"char": "↔", "name": "Left right arrow"},
        '¬': {"char": "←", "name": "Leftwards arrow"},
        '­': {"char": "↑", "name": "Upwards arrow"},
        '®': {"char": "→", "name": "Rightwards arrow"},
        '¯': {"char": "↓", "name": "Downwards arrow"},
        '¿': {"char": "↵", "name": "Downwards arrow with corner leftwards"},
        'Û': {"char": "⇔", "name": "Left right double arrow"},
        'Ü': {"char": "⇐", "name": "Leftwards double arrow"},
        'Ý': {"char": "⇑", "name": "Upwards double arrow"},
        'Þ': {"char": "⇒", "name": "Rightwards double arrow"},
        'ß': {"char": "⇓", "name": "Downwards double arrow"},
        '"': {"char": "∀", "name": "For all"},
        '$': {"char": "∃", "name": "There exists"},
        "'": {"char": "∍", "name": "Small contains as member"},
        '*': {"char": "∗", "name": "Asterisk operator"},
        '-': {"char": "−", "name": "Minus sign"},
        '@': {"char": "≅", "name": "Approximately equal to"},
        '\\': {"char": "∴", "name": "Therefore"},
        '^': {"char": "⊥", "name": "Up tack"},
        '~': {"char": "∼", "name": "Tilde operator"},
        '£': {"char": "≤", "name": "Less-than or equal to"},
        '¥': {"char": "∞", "name": "Infinity"},
        '³': {"char": "≥", "name": "Greater-than or equal to"},
        'µ': {"char": "∝", "name": "Proportional to"},
        '¶': {"char": "∂", "name": "Partial differential"},
        '·': {"char": "•", "name": "Bullet"},
        '¹': {"char": "≠", "name": "Not equal to"},
        'º': {"char": "≡", "name": "Identical to"},
        '»': {"char": "≈", "name": "Almost equal to"},
        'Ä': {"char": "⊗", "name": "Circled times"},
        'Å': {"char": "⊕", "name": "Circled plus"},
        'Æ': {"char": "∅", "name": "Empty set"},
        'Ç': {"char": "∩", "name": "Intersection"},
        'È': {"char": "∪", "name": "Union"},
        'É': {"char": "⊃", "name": "Superset of"},
        'Ê': {"char": "⊇", "name": "Superset of or equal to"},
        'Ë': {"char": "⊄", "name": "Not a subset of"},
        'Ì': {"char": "⊂", "name": "Subset of"},
        'Í': {"char": "⊆", "name": "Subset of or equal to"},
        'Î': {"char": "∈", "name": "Element of"},
        'Ï': {"char": "∉", "name": "Not an element of"},
        'Ð': {"char": "∠", "name": "Angle"},
        'Ñ': {"char": "∇", "name": "Nabla"},
        'Õ': {"char": "∏", "name": "N-ary product"},
        'Ö': {"char": "√", "name": "Square root"},
        '×': {"char": "⋅", "name": "Dot operator"},
        'Ù': {"char": "∧", "name": "Logical and"},
        'Ú': {"char": "∨", "name": "Logical or"},
        'å': {"char": "∑", "name": "N-ary summation"},
        'ò': {"char": "∫", "name": "Integral"},
        '½': {"char": "⏐", "name": "Vertical line extension"},
        '¾': {"char": "⎯", "name": "Horizontal line extension"},
        'á': {"char": "〈", "name": "Left-pointing angle bracket"},
        'æ': {"char": "⎛", "name": "Left parenthesis upper hook"},
        'ç': {"char": "⎜", "name": "Left parenthesis extension"},
        'è': {"char": "⎝", "name": "Left parenthesis lower hook"},
        'é': {"char": "⎡", "name": "Left square bracket upper corner"},
        'ê': {"char": "⎢", "name": "Left square bracket extension"},
        'ë': {"char": "⎣", "name": "Left square bracket lower corner"},
        'ì': {"char": "⎧", "name": "Left curly bracket upper hook"},
        'í': {"char": "⎨", "name": "Left curly bracket middle piece"},
        'î': {"char": "⎩", "name": "Left curly bracket lower hook"},
        'ï': {"char": "⎪", "name": "Curly bracket extension"},
        'ñ': {"char": "〉", "name": "Right-pointing angle bracket"},
        'ó': {"char": "⌠", "name": "Top half integral"},
        'ô': {"char": "⎮", "name": "Integral extension"},
        'õ': {"char": "⌡", "name": "Bottom half integral"},
        'ö': {"char": "⎞", "name": "Right parenthesis upper hook"},
        '÷': {"char": "⎟", "name": "Right parenthesis extension"},
        'ø': {"char": "⎠", "name": "Right parenthesis lower hook"},
        'ù': {"char": "⎤", "name": "Right square bracket upper corner"},
        'ú': {"char": "⎥", "name": "Right square bracket extension"},
        'û': {"char": "⎦", "name": "Right square bracket lower corner"},
        'ü': {"char": "⎫", "name": "Right curly bracket upper hook"},
        'ý': {"char": "⎬", "name": "Right curly bracket middle piece"},
        'þ': {"char": "⎭", "name": "Right curly bracket lower hook"},
        'à': {"char": "◊", "name": "Lozenge"},
        '§': {"char": "♣", "name": "Black club suit"},
        '¨': {"char": "♦", "name": "Black diamond suit"},
        '©': {"char": "♥", "name": "Black heart suit"},
        'ª': {"char": "♠", "name": "Black spade suit"},        
    }

    def transform(self, data):
        raw, xml = data

        for node in xml.xpath(".//font-face-symbol"):
            item = self.FONTFACESYMBOL.get(node.text)
            if item:
                node.text = item["char"]
                node.tag = "REMOVEFONTFACESYMBOL"

        ET.strip_tags(xml, "REMOVEFONTFACESYMBOL")
        return data

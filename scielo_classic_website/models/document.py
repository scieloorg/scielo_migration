import logging

from scielo_classic_website.isisdb.meta_record import MetaRecord
from scielo_classic_website.isisdb.h_record import DocumentRecord
from scielo_classic_website.isisdb.p_record import ParagraphRecord
from scielo_classic_website.isisdb.c_record import ReferenceRecord
from scielo_classic_website.models.journal import Journal
from scielo_classic_website.models.issue import Issue
from scielo_classic_website.models.reference import Reference
from scielo_classic_website.models.html_body import (
    BodyFromISIS,
    BodyFromHTMLFile,
)
from scielo_classic_website.spsxml.sps_xml_pipes import get_xml_rsps
from scielo_classic_website.spsxml import sps_xml_body_pipes


RECORD = dict(
    o=DocumentRecord,
    h=DocumentRecord,
    f=DocumentRecord,
    l=MetaRecord,
    c=ReferenceRecord,
    p=ParagraphRecord,
)


def _get_value(data, tag):
    """
    Returns first value of field `tag`
    """
    # data['v880'][0]['_']
    try:
        _data = data[tag][0]
        if len(_data) > 1:
            return _data
        else:
            return _data['_']
    except (KeyError, IndexError):
        return None


class Document:
    def __init__(self, data, _id=None):
        """
        Parameters
        ----------
            data : dict
                keys:
                    article
                    title
                    issue
                    fulltexts (list of dict: uri, uri_text, lang, )
        """
        self.data = {}
        try:
            self.data['article'] = data['article']
        except KeyError:
            self.data['article'] = data
        self.document_records = DocumentRecords(self.data['article'], _id)
        self._h_record = self.document_records.article_meta
        self.body_from_isis = BodyFromISIS(
            self.document_records.get_record("p")
        )
        try:
            self._journal = Journal(data["title"])
        except KeyError:
            self._journal = None
        try:
            self._issue = Issue(data["issue"])
        except KeyError:
            self._issue = None
        self.xml_from_html = None

    def __getattr__(self, name):
        # desta forma Document não precisa herdar de DocumentRecord
        # fica menos acoplado
        if hasattr(self._h_record, name):
            return getattr(self._h_record, name)
        raise AttributeError(f"Document.{name} does not exist")

    @property
    def main_html_paragraphs(self):
        # list of dict keys: part, text, index, reference_index
        if self.document_records.get_record("p"):
            return {
                "before references": list(
                    self.body_from_isis.before_references_items),
                "references": list(
                    self.body_from_isis.references_items),
                "after references": list(
                    self.body_from_isis.after_references_items),
            }

    @property
    def translated_html_by_lang(self):
        """
        {
            "en": {
                "before references": html,
                "after references": html,
            },
            "es": {
                "before references": html,
                "after references": html,
            }
        }
        """
        return self._translated_html_by_lang

    def add_translated_html(self, lang, before_references, after_references):
        """
        {
            "en": {
                "before references": html,
                "after references": html,
            },
            "es": {
                "before references": html,
                "after references": html,
            }
        }
        """
        if not hasattr(self, '_translated_html_by_lang') or not self._translated_html_by_lang:
            self._translated_html_by_lang = {}
        self._translated_html_by_lang[lang] = {
            "before references": before_references,
            "after references": after_references,
        }

    @property
    def journal(self):
        return self._journal

    @property
    def issue(self):
        return self._issue

    @journal.setter
    def journal(self, record):
        self._journal = Journal(record)

    @issue.setter
    def issue(self, record):
        self._issue = Issue(record)

    @property
    def start_page(self):
        return self.page.get("start")

    @property
    def end_page(self):
        return self.page.get("end")

    @property
    def start_page_sequence(self):
        return self.page.get("sequence")

    @property
    def fpage(self):
        return self.page.get("start")

    @property
    def lpage(self):
        return self.page.get("end")

    @property
    def fpage_seq(self):
        return self.page.get("sequence")

    @property
    def elocation(self):
        return self.page.get("elocation")

    def get_section(self, lang):
        if not hasattr(self, '_sections') and not self._sections:
            self._sections = {}
            for item in self.issue.get_sections(self.section_code):
                self._sections[item['lang']] = item
        try:
            return self._sections[lang]['text']
        except KeyError:
            return None

    def get_article_title(self, lang):
        if not hasattr(self, '_article_titles') and not self._article_titles:
            self._article_titles = {}
            for item in self.translated_titles:
                self._article_titles[item['lang']] = item
        try:
            return self._article_titles[lang]['text']
        except KeyError:
            return None

    def get_abstract(self, lang):
        if not hasattr(self, '_abstracts') and not self._abstracts:
            self._abstracts = {}
            for item in self.translated_abstracts:
                self._abstracts[item['lang']] = item
        try:
            return self._abstracts[lang]['text']
        except KeyError:
            return None

    def get_keywords_group(self, lang):
        if not hasattr(self, '_keywords_groups') and not self._keywords_groups:
            self._keywords_groups = self._h_record.keywords_groups
        try:
            return self._keywords_groups[lang]
        except KeyError:
            return None

    @property
    def translated_htmls(self):
        _translated_htmls = (self.data.get("body") or {}).copy()
        try:
            del _translated_htmls[self.original_language]
        except KeyError:
            pass
        return _translated_htmls

    @property
    def isis_updated_date(self):
        return self.update_date

    @property
    def isis_created_date(self):
        return self.creation_date

    @property
    def permissions(self):
        # FIXME
        return {"url": "", "text": ""}

    @property
    def authors_with_aff(self):
        affs = {
            item['id']: item
            for item in self.affiliations
        }
        for author in self.authors:
            author['affiliation'] = affs[author['xref']]['orgname']
            yield author

    @property
    def citations(self):
        for record in self.document_records.get_record("c"):
            yield Reference(record)

    def generate_body_and_back_from_html(self, html_texts=None):
        """
        Parameters
        ----------
        html_texts : {
            lang: {
                "before references": before,
                "after references": after,
                }
            }
        """
        if not self.main_html_paragraphs:
            logging.info("generate_body_and_back_from_html: No main HTML found")
            return
        langs = {}
        # obtém os textos html
        html_texts = html_texts or {}
        for lang, html_text in html_texts.items():
            logging.info("generate_body_and_back_from_html %s" % lang)
            document.add_translated_html(
                lang,
                html_text['before references'],
                html_text['after references']
            )
        return sps_xml_body_pipes.convert_html_to_xml(self)

    def generate_full_xml(self, selected_xml_body=None):
        """
        Parameters
        ----------
        html_texts : {
            lang: {
                "before references": before,
                "after references": after,
                }
            }
        """
        if not self.main_html_paragraphs:
            return
        self.xml_body = selected_xml_body
        return get_xml_rsps(self)


class DocumentRecords:
    def __init__(self, records, _id=None):
        self._id = _id
        self._records = None
        self.records = records

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, _records):
        self._records = {}
        for _record in _records:
            meta_record = MetaRecord(_record)
            rec_type = meta_record.rec_type
            try:
                record = RECORD[rec_type](_record)
                self._records[rec_type] = self._records.get(rec_type) or []
                self._records[rec_type].append(record)
            except KeyError:
                pass

    def get_record(self, rec_type):
        return self._records.get(rec_type)

    @property
    def article_meta(self):
        try:
            return self._records.get("f")[0]
        except TypeError:
            return None

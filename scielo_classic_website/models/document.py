import logging
from functools import cached_property

from lxml import etree as ET

from scielo_classic_website.htmlbody.html_body import BodyFromISIS
from scielo_classic_website.isisdb.c_record import ReferenceRecord
from scielo_classic_website.isisdb.h_record import DocumentRecord
from scielo_classic_website.isisdb.meta_record import MetaRecord
from scielo_classic_website.isisdb.p_record import ParagraphRecord
from scielo_classic_website.models.issue import Issue
from scielo_classic_website.models.journal import Journal
from scielo_classic_website.models.reference import Reference
from scielo_classic_website.spsxml import sps_xml_body_pipes
from scielo_classic_website.spsxml.sps_xml_pipes import get_xml_rsps
from scielo_classic_website.exceptions import GetSectionTitleException


RECORD = dict(
    o=DocumentRecord,
    h=DocumentRecord,
    f=DocumentRecord,
    l=MetaRecord,
    c=ReferenceRecord,
    p=ParagraphRecord,
)


class GenerateBodyAndBackFromHTMLError(Exception): ...


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
            return _data["_"]
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
        self._body_from_isis = None
        self.xml_from_html = None
        self._translated_html_by_lang = {}
        self._main_html_paragraphs = {}
        self._document_records = None
        self.xml_body_and_back = None
        self.xml_body = None
        self.exceptions = None
        self.pretty_print = False
        self.data = {}
        try:
            self.data["article"] = data["article"]
        except (TypeError, KeyError):
            self.data["article"] = data
        try:
            self._journal = Journal(data["title"])
        except (TypeError, KeyError):
            self._journal = None
        try:
            self._issue = Issue(data["issue"])
        except (TypeError, KeyError):
            self._issue = None
        self.document_records = DocumentRecords(
            self.data["article"], _id, self.data.get("paragraph")
        )
        self._params_for_xml_creation = {}

    def __getattr__(self, name):
        # desta forma Document não precisa herdar de DocumentRecord
        # fica menos acoplado

        if hasattr(self.h_record, name):
            return getattr(self.h_record, name)
        raise AttributeError(f"{type(self.h_record)}.{name} does not exist")

    @property
    def params_for_xml_creation(self):
        return self._params_for_xml_creation

    @params_for_xml_creation.setter
    def params_for_xml_creation(self, params):
        if isinstance(params, dict):
            self._params_for_xml_creation = params
        else:
            raise TypeError("Document.params_for_xml_creation must be dict")

    @property
    def record_types(self):
        return self.document_records.records.keys()

    @property
    def document_records(self):
        return self._document_records

    @document_records.setter
    def document_records(self, document_records):
        self._document_records = document_records

    @cached_property
    def processing_date(self):
        try:
            item = self.document_records.get_record("o")[0]
            return item.processing_date
        except (KeyError, IndexError):
            return None

    @cached_property
    def h_record(self):
        try:
            return self.document_records.get_record("f")[0]
        except TypeError as e:
            if len(self.document_records._records.keys()) == 0:
                try:
                    logging.info(f"Document.h_record: {self.data['article']}")
                except KeyError:
                    logging.info(f"Document.h_record: {self.data.keys()}")
            else:
                logging.info(
                    f"Document.h_record: {self.document_records._records.keys()}"
                )
            logging.exception(e)

    @cached_property
    def p_records(self):
        return self.document_records.get_record("p") or []

    @cached_property
    def main_html_paragraphs(self):
        if not self.p_records:
            return {}
        try:
            return BodyFromISIS(self.p_records).parts
        except Exception as e:
            logging.info("main_html_paragraphs")
            logging.exception(e)
            return {}

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
        return self._translated_html_by_lang or {}

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

    @cached_property
    def page(self):
        return self.h_record.page

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

    def get_sections(self):
        items = {}
        for item in self.issue.get_sections(self.section_code):
            items[item["language"]] = item
        return items

    def get_section_title(self, lang):
        try:
            sections = self.get_sections()
            section = sections.get(lang)
            return section["text"]
        except (TypeError, ValueError, KeyError):
            raise GetSectionTitleException(
                f"Not registered: {self.section_code} {lang}. Registered: {self.issue.sections}"
            )

    def get_article_title(self, lang):
        if not hasattr(self, "_article_titles") or not self._article_titles:
            self._article_titles = {}
            for item in self.translated_titles:
                self._article_titles[item["language"]] = item
        try:
            return self._article_titles[lang]["text"]
        except KeyError:
            return None

    def get_abstract(self, lang):
        if not hasattr(self, "_abstracts") or not self._abstracts:
            self._abstracts = {}
            for item in self.translated_abstracts:
                self._abstracts[item["language"]] = item
        try:
            return self._abstracts[lang]["text"]
        except KeyError:
            return None

    def get_keywords_group(self, lang):
        if not hasattr(self, "_keywords_groups") or not self._keywords_groups:
            self._keywords_groups = self.h_record.keywords_groups
        try:
            return self._keywords_groups[lang]
        except KeyError:
            return None

    @property
    def isis_updated_date(self):
        return self.h_record.update_date

    @property
    def isis_created_date(self):
        return self.h_record.creation_date

    @property
    def permissions(self):
        return self.get_license("en")

    def get_license(self, language):
        try:
            return self.license_texts[language]
        except KeyError:
            return None

    @property
    def license_texts(self):
        languages = ("en", "es", "pt")
        license_code = self.h_record.license_code
        issue_licenses = self.issue.license_texts
        data = {}
        for language in languages:
            item = issue_licenses.get(language) or {}
            item["code"] = license_code
            data.setdefault(language, item)
            try:
                text = f"<root>{item['html']}</root>"
                html = ET.fromstring()
                item["url"] = html.get("href")
                item["text"] = "".join(html.itertext())
                data[language] = item
            except Exception as e:
                logging.exception(e)
        return data

    @property
    def authors_with_aff(self):
        affs = {item["id"]: item for item in self.affiliations}
        for author in self.authors:
            author["affiliation"] = affs[author["xref"]]["orgname"]
            yield author

    @cached_property
    def citations(self):
        return self.document_records.get_record("c")

    def generate_body_and_back_from_html(self, translated_texts=None):
        """
        Parameters
        ----------
        translated_texts : {
            lang: {
                "before references": before,
                "after references": after,
                }
            }
        """
        translations = False
        for lang, parts in (translated_texts or {}).items():
            text = "".join(parts.values())
            if text:
                translations = True
                break

        main_text = False
        for part_name, part_items in (self.main_html_paragraphs or {}).items():
            if part_items:
                main_text = True
                break

        if main_text or translations:
            sps_xml_body_pipes.convert_html_to_xml(self)

    def generate_full_xml(self, selected_xml_body=None):
        """
        Parameters
        ----------
        selected_xml_body : str
        """
        try:
            self.xml_body = selected_xml_body or self.xml_body_and_back[-1]
        except (TypeError, IndexError) as e:
            self.xml_body = None
        return get_xml_rsps(self)


class DocumentRecords:
    def __init__(self, records, _id=None, paragraph_records=None):
        self.paragraph_records = paragraph_records
        self._id = _id
        self._records = None
        self.records = records

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, _records):
        self._records = {}
        for _record in _records or []:
            meta_record = MetaRecord(_record)
            rec_type = meta_record.rec_type
            if not rec_type:
                continue
            try:
                record = RECORD[rec_type](_record)
                self._records[rec_type] = self._records.get(rec_type) or []
                self._records[rec_type].append(record)
            except KeyError as e:
                # todos os registros são armazenados, no entanto,
                # durante a migração nem todos os registros são usados
                pass
        if not self._records.get("p") and self.paragraph_records:
            self._records["p"] = []
            for _record in self.paragraph_records:
                record = ParagraphRecord(_record)
                self._records["p"].append(record)

    def get_record(self, rec_type):
        return self._records.get(rec_type)

    @property
    def article_meta(self):
        return self._records.get("f")[0]

    @property
    def stats(self):
        for label, records in self.records.items():
            yield {"record_type": label, "count": len(records)}

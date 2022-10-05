from scielo_classic_website.isisdb.meta_record import MetaRecord
from scielo_classic_website.isisdb.h_record import DocumentRecord
from scielo_classic_website.isisdb.p_record import ParagraphRecord
from scielo_classic_website.models.journal import Journal
from scielo_classic_website.models.issue import Issue
from scielo_classic_website.models.html_body import (
    BodyFromISIS,
    BodyFromHTMLFile,
)


RECORD = dict(
    o=DocumentRecord,
    h=DocumentRecord,
    f=DocumentRecord,
    l=MetaRecord,
    c=DocumentRecord,
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

    def __getattr__(self, name):
        # desta forma Document não precisa herdar de DocumentRecord
        # fica menos acoplado
        if hasattr(self._h_record, name):
            return getattr(self._h_record, name)
        raise AttributeError(f"Document.{name} does not exist")

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

    @property
    def translated_htmls(self):
        _translated_htmls = (self.data.get("body") or {}).copy()
        try:
            del _translated_htmls[self.original_language]
        except KeyError:
            pass
        return _translated_htmls

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

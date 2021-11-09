from scielo_migration.iid2json.meta_record import MetaRecord
from scielo_migration.isisdb.h_record import ArticleRecord


RECORD = dict(
    o=ArticleRecord,
    h=ArticleRecord,
    f=ArticleRecord,
    l=MetaRecord,
    c=ArticleRecord,
)


class Journal:
    def __init__(self, journal_record):
        self.journal_record = journal_record

    def __getattr__(self, name):
        # desta forma Journal não precisa herdar de JournalRecord
        # fica menos acoplado
        if hasattr(self.journal_record, name):
            return getattr(self.journal_record, name)
        raise AttributeError(name)


class Document:
    def __init__(self, h_record, journal=None, issue=None, citations=None):
        self.h_record = h_record
        self.journal = journal
        self.issue = issue
        self.citations = citations

    def __getattr__(self, name):
        # desta forma Document não precisa herdar de ArticleRecord
        # fica menos acoplado
        if hasattr(self.h_record, name):
            return getattr(self.h_record, name)
        raise AttributeError(name)


class DocumentRecords:
    def __init__(self, _id, records):
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
            record = RECORD[rec_type](_record)
            self._records[rec_type] = self._records.get(rec_type) or []
            self._records[rec_type].append(record)

    def get_record(self, rec_type):
        return self._records.get(rec_type)

    @property
    def article_meta(self):
        try:
            return self._records.get("f")[0]
        except TypeError:
            return None

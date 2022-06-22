from scielo_classic_website.isisdb.meta_record import MetaRecord


class Journal:
    def __init__(self, journal_record):
        self.journal_record = journal_record

    def __getattr__(self, name):
        # desta forma Journal não precisa herdar de JournalRecord
        # fica menos acoplado
        if hasattr(self.journal_record, name):
            return getattr(self.journal_record, name)
        raise AttributeError(name)

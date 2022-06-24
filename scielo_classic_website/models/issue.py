from scielo_classic_website.isisdb.issue_record import IssueRecord


class Issue:
    def __init__(self, _record):
        self._record = _record
        self.issue_record = IssueRecord(_record)

    def __getattr__(self, name):
        # desta forma Issue não precisa herdar de IssueRecord
        # fica menos acoplado
        if hasattr(self.issue_record, name):
            return getattr(self.issue_record, name)
        raise AttributeError(name)

    @property
    def record(self):
        return self._record

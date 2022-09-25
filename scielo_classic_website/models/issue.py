import logging

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
        raise AttributeError(f"classic_website.Issue has no attribute {name}")

    @property
    def record(self):
        return self._record

    @property
    def publication_year(self):
        return self.issue_record.publication_date[:4]

    @property
    def supplement(self):
        return self.supplement_volume or self.supplement_number

    @property
    def suppl(self):
        return self.supplement_volume or self.supplement_number

    @property
    def order(self):
        return self.issue_record.order[:4] + self.issue_record.order[4:].zfill(4)

    @property
    def pid(self):
        # 0001-371419980003
        return self.journal + self.order

    @property
    def isis_created_date(self):
        return self.issue_record.creation_date

    @property
    def isis_updated_date(self):
        return self.issue_record.update_date

    @property
    def issue_label(self):
        pr = self.is_press_release or ''
        if self.number in ("ahead", "review"):
            return self.publication_year + "n" + self.number + pr
        return "".join([
            k + v
            for k, v in zip(("v", "n", "s", ""), (self.volume, self.number, self.suppl, pr))
            if v
            ])


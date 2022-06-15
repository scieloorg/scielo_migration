from scielo_migration.isisdb import models


class Journal(models.Journal):
    def __init__(self, data):
        super().__init__(data)


class Article(models.Document):

    def __init__(self, data):
        super().__init__(data)

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
    def elocation(self):
        return self.page.get("elocation")

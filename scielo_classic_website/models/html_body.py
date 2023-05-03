from scielo_classic_website.utils.files_utils import read_file


class BodyFromISIS:
    """
    Interface amigável para obter os dados da base isis
    que estão no formato JSON
    """

    def __init__(self, p_records):
        self.p_records = p_records or []
        self.first_reference = None
        self.last_reference = None
        self._identify_references_range()

    @property
    def before_references_items(self):
        for item in self.before_references_paragraphs:
            # record_type_index, text, record_type, reference_index
            data = item.data
            data["part"] = "before references"
            yield data

    @property
    def reference_items(self):
        for item in self.reference_paragraphs:
            # record_type_index, text, record_type, reference_index
            data = item.data
            data["part"] = "reference"
            yield data

    @property
    def after_references_items(self):
        for item in self.after_references_paragraphs:
            # record_type_index, text, record_type, reference_index
            data = item.data
            data["part"] = "after references"
            yield data

    @property
    def before_references_paragraphs(self):
        return self.p_records[: self.first_reference]

    @property
    def reference_paragraphs(self):
        return self.p_records[self.first_reference : self.last_reference + 1]

    @property
    def after_references_paragraphs(self):
        return self.p_records[self.last_reference + 1 :]

    def _identify_references_range(self):
        for i, item in enumerate(self.p_records):
            if not self.first_reference and item.reference_index:
                self.first_reference = i
            if item.reference_index:
                self.last_reference = i

    @property
    def references_text(self):
        return "".join([item.paragraph_text for item in self.reference_paragraphs])

    @property
    def text(self):
        return "".join([item.paragraph_text for item in self.p_records])


class HTMLFile:
    """ """

    def __init__(self, file_path):
        self._content = read_file(file_path, encoding="iso-8859-1")

    @property
    def body_content(self):
        p = self._content.find("<body")
        if not p:
            return ""
        b = self._content[p:]
        b = b[b.find(">") + 1 :]
        b = b[: b.find("</body>")]
        return b


class BodyFromHTMLFile:
    """
    Interface amigável para obter os dados da base isis
    que estão no formato JSON
    """

    def __init__(
        self,
        before_references_file_path,
        reference_texts=None,
        after_references_file_path=None,
    ):
        self.before_references = HTMLFile(before_references_file_path)
        self.after_references = None
        if after_references_file_path:
            self.after_references = HTMLFile(after_references_file_path)
        self.reference_texts = reference_texts or ""

    @property
    def text(self):
        return "".join(
            [
                self.before_references.body_content,
                self.reference_texts,
                self.after_references and self.after_references.body_content or "",
            ]
        )

    @property
    def html(self):
        return f"<html><body>{self.text}</body></html>"

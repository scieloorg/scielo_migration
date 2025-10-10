import logging
from functools import cached_property

from scielo_classic_website.htmlbody import html_style_fixer
from scielo_classic_website.isisdb.c_record import ReferenceRecord


def html_decode(text):
    # TODO https://github.com/scieloorg/xylose/blob/262126e37e55bb7df2ebc585472f260daddedce9/xylose/scielodocument.py#L124
    return text


class Reference:
    def __init__(self, reference_record=None, fix_function=None):
        self._reference_record = reference_record
        self._reference_record.fix_function = lambda x: x

    def __getattr__(self, name):
        # desta forma Reference não precisa herdar de ReferenceRecord
        # fica menos acoplado
        if hasattr(self._reference_record, name):
            return getattr(self._reference_record, name)
        raise AttributeError(f"classic_website.Reference has no attribute {name}")

    @property
    def record(self):
        return self._reference_record.record

    @cached_property
    def publication_type(self):
        """
        This method retrieves the publication type of the citation.
        """
        return self._reference_record.publication_type

    @cached_property
    def pagination(self):
        """
        Internal method to process pages information.
        Returns a tuple with (start_page, end_page, elocation, pages_range)
        """
        elocation = None
        start_page = None
        end_page = None
        pages_range = None
        
        for page in self._reference_record.pages:
            start_page = page.get("first")
            end_page = page.get("last")
            elocation = page.get("elocation")
            pages_range = page.get("range")
            return (start_page, end_page, elocation, pages_range)

        pages_range_data = self._reference_record.pages_range
        elocation = elocation or pages_range_data.get("elocation")
        pages_range = pages_range_data.get("range")
        
        if pages_range:
            start_page = pages_range.split("-")[0]
            end_page = pages_range.split("-")[-1]
        else:
            start_page = None
            end_page = None
            
        return (start_page, end_page, elocation, pages_range)

    @property
    def start_page(self):
        """
        This method retrieves the start page of the citation.
        This method deals with the legacy fields (514 and 14).
        """
        return self.pagination[0]

    @property
    def end_page(self):
        """
        This method retrieves the end page of the citation.
        This method deals with the legacy fields (514 and 14).
        """
        return self.pagination[1]

    @property
    def elocation(self):
        """
        This method retrieves the e-location of the citation.
        This method deals with the legacy fields (514 and 14).
        """
        return self.pagination[2]

    @property
    def pages(self):
        """
        This method retrieves the start and end page of the citation
        separeted by hipen.
        This method deals with the legacy fields (514 and 14).
        """
        return self.pagination[3]

    @cached_property
    def source(self):
        """
        This method retrieves the citation source title. Ex:
        Journal: Journal of Microbiology
        Book: Alice's Adventures in Wonderland
        """
        return (
            self.journal_title
            or self._reference_record.monographic_title
            and self._reference_record.monographic_title.get("text")
        )

    @cached_property
    def journal_title(self):
        """
        This method retrieves the citation source title. Ex:
        Journal: Journal of Microbiology
        Book: Alice's Adventures in Wonderland
        """
        return (
            self._reference_record.journal_title
            and self._reference_record.journal_title.get("text")
        )

    @cached_property
    def article_title(self):
        """
        If it is an article citation, this method retrieves the article title, if it exists.
        """
        if self.publication_type != "book":
            return (
                self._reference_record.article_title
                and self._reference_record.article_title.get("text")
            )

    @cached_property
    def chapter_title(self):
        """
        If it is an book citation, this method retrieves the chapter title, if it exists.
        """
        if self.publication_type == "book":
            return (
                self._reference_record.article_title
                and self._reference_record.article_title.get("text")
            )

    @cached_property
    def data_title(self):
        """
        If it is an data citation, this method retrieves the data title, if it exists.
        """
        if self.publication_type == "data":
            return self._reference_record.article_title.get("text")

    @cached_property
    def date(self):
        """
        This method retrieves the date, if it is exists, according to the
        reference type
        Se é desejável obter a data de publicação, usar: self.publication_date
        """
        if self.publication_type == "confproc":
            return self._reference_record.conference_date_iso
        if self.publication_type == "thesis":
            return self._reference_record.thesis_date_iso
        if self.publication_type == "webpage":
            return self._reference_record.access_date_iso
        if self.publication_type == "patent":
            return self.patent_application_date_iso
        return self._reference_record.publication_date_iso

    @cached_property
    def publication_date(self):
        """
        This method retrieves the publication date, if it is exists.
        Retorna outras datas no lugar para minimizar problemas de marcação
        incorreta
        """
        return (
            self._reference_record.publication_date_iso
            or self._reference_record.conference_date_iso
            or self._reference_record.thesis_date_iso
            or self.patent_application_date_iso
            or self._reference_record.access_date_iso
        )

    @cached_property
    def patent_application_date(self):
        try:
            return self._reference_record.patent.get("date")
        except AttributeError:
            return None

    @cached_property
    def patent_application_date_iso(self):
        try:
            return self._reference_record.patent.get("date_iso")
        except AttributeError:
            return None

    @cached_property
    def patent_country(self):
        country = self._reference_record.patent.get("country")
        return country if country != "nd" else None

    @cached_property
    def patent_organization(self):
        return self._reference_record.patent.get("organization")

    @cached_property
    def patent_id(self):
        return self._reference_record.patent.get("id")

    @cached_property
    def mixed_citation(self):
        if self.paragraph_text:
            return html_style_fixer.get_mixed_citation_node(self.paragraph_text)
import logging
from functools import lru_cache

from scielo_classic_website.isisdb.raw_record import RawRecord


class BaseReferenceRecord(RawRecord):
    def __init__(self, record):
        super().__init__(record)

    @property
    @lru_cache(maxsize=1)
    def analytic_person_authors(self):
        """
        Analytic Anonymous
        v010 {'_': 'anonymous', 'n': 'given_names', 'p': 'prefix', 'r': 'role', 's': 'surname'}
        Returns:
        {'anonymous': '', 'given_names': '', 'prefix': '', 'role': '', 'surname': ''}
        """
        return self.get_field_content(
            "v010",
            {
                "_": "anonymous",
                "n": "given_names",
                "p": "prefix",
                "r": "role",
                "s": "surname",
            },
            False,
        )

    @property
    @lru_cache(maxsize=1)
    def analytic_corporative_authors(self):
        """
        Analytic Corporative Author
        v011 {'_': 'name', 'd': 'division'}
        Returns:
        {'name': '', 'division': ''}
        """
        return self.get_field_content(
            "v011", {"_": "name", "d": "division"}, False
        )

    @property
    @lru_cache(maxsize=1)
    def article_title(self):
        """
        Article Title
        v012 {'_': 'text', 'l': 'language'}
        Returns:
        {'text': '', 'language': ''}
        """
        return self.get_field_content(
            "v012", {"_": "text", "l": "language"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def pages_range(self):
        """
        v014 {'_': 'range', 'e': 'elocation'}
        Returns:
        {'range': '', 'elocation': ''}
        """
        return self.get_field_content(
            "v014", {"_": "range", "e": "elocation"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def monographic_person_authors(self):
        """
        Monographic Anonymous
        v016 {'_': 'anonymous', 'n': 'given_names', 'p': 'prefix', 'r': 'role', 's': 'surname'}
        Returns:
        {'anonymous': '', 'given_names': '', 'prefix': '', 'role': '', 'surname': ''}
        """
        return self.get_field_content(
            "v016",
            {
                "_": "anonymous",
                "n": "given_names",
                "p": "prefix",
                "r": "role",
                "s": "surname",
            },
            False,
        )

    @property
    @lru_cache(maxsize=1)
    def monographic_corporative_authors(self):
        """
        Monographic Corporative Author
        v017 {'_': 'name', 'd': 'division'}
        Returns:
        {'name': '', 'division': ''}
        """
        return self.get_field_content(
            "v017", {"_": "name", "d": "division"}, False
        )

    @property
    @lru_cache(maxsize=1)
    def monographic_title(self):
        """
        Monographic Title
        v018 {'_': 'text', 'l': 'language'}
        Returns:
        {'text': '', 'language': ''}
        """
        return self.get_field_content(
            "v018", {"_": "text", "l": "language"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def size(self):
        """
        Size
        v020 {'_': 'size', 'u': 'unit'}
        Returns:
        {'size': '', 'unit': ''}
        """
        return self.get_field_content(
            "v020", {"_": "size", "u": "unit"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def tome(self):
        """
        v022
        """
        return self.get_field_content("v022", {}, True)

    @property
    @lru_cache(maxsize=1)
    def coltitle(self):
        """
        Collection title
        v025
        """
        return self.get_field_content("v025", {}, True)

    @property
    @lru_cache(maxsize=1)
    def colvolid(self):
        """
        Collection volume
        v026
        """
        return self.get_field_content("v026", {}, True)

    @property
    @lru_cache(maxsize=1)
    def serial_person_authors(self):
        """
        Monographic Anonymous
        v028 {'_': 'anonymous', 'n': 'given_names', 'p': 'prefix', 'r': 'role', 's': 'surname'}
        Returns:
        {'anonymous': '', 'given_names': '', 'prefix': '', 'role': '', 'surname': ''}
        """
        return self.get_field_content(
            "v028",
            {
                "_": "anonymous",
                "n": "given_names",
                "p": "prefix",
                "r": "role",
                "s": "surname",
            },
            False,
        )

    @property
    @lru_cache(maxsize=1)
    def serial_corporative_authors(self):
        """
        Monographic Corporative Author
        v029 {'_': 'name', 'd': 'division'}
        Returns:
        {'name': '', 'division': ''}
        """
        return self.get_field_content(
            "v029", {"_": "name", "d": "division"}, False
        )

    @property
    @lru_cache(maxsize=1)
    def journal_title(self):
        """
        Journal title
        v030 {'_': 'text', 'l': 'language'}
        Returns:
        {'text': '', 'language': ''}
        """
        return self.get_field_content(
            "v030", {"_": "text", "l": "language"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def volume(self):
        """
        Volume
        v031
        """
        return self.get_field_content("v031", {}, True)

    @property
    @lru_cache(maxsize=1)
    def issue(self):
        """
        Issue
        v032 {'n': 'number', 's': 'suppl'}
        Returns:
        {'number': '', 'suppl': ''}
        """
        return self.get_field_content(
            "v032", {"n": "number", "s": "suppl"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def issue_title(self):
        """
        Issue title
        v033
        """
        return self.get_field_content("v033", {}, True)

    @property
    @lru_cache(maxsize=1)
    def issue_part(self):
        """
        Issue part
        v034
        """
        return self.get_field_content("v034", {}, True)

    @property
    @lru_cache(maxsize=1)
    def issn(self):
        """
        ISSN
        v035
        """
        return self.get_field_content("v035", {}, True)

    @property
    @lru_cache(maxsize=1)
    def ext_link(self):
        """
        Ext Link
        v037
        """
        return self.get_field_content("v037", {}, True)

    @property
    @lru_cache(maxsize=1)
    def thesis_date(self):
        """
        Thesis Date
        v044
        """
        return self.get_field_content("v044", {}, True)

    @property
    @lru_cache(maxsize=1)
    def thesis_date_iso(self):
        """
        Thesis Date Iso
        v045
        """
        return self.get_field_content("v045", {}, True)

    @property
    @lru_cache(maxsize=1)
    def thesis_location(self):
        """
        Thesis Location
        v046 {'_': 'city', 'e': 'state'}
        Returns:
        {'city': '', 'state': ''}
        """
        return self.get_field_content(
            "v046", {"_": "city", "e": "state"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def thesis_country(self):
        """
        Thesis Country
        v047
        """
        return self.get_field_content("v047", {}, True)

    @property
    @lru_cache(maxsize=1)
    def thesis_organization(self):
        """
        Thesis Organization
        v050 {'_': 'name', 'd': 'division'}
        Returns:
        {'name': '', 'division': ''}
        """
        return self.get_field_content(
            "v050", {"_": "name", "d": "division"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def thesis_degree(self):
        """
        Thesis Degree
        v051
        """
        return self.get_field_content("v051", {}, True)

    @property
    @lru_cache(maxsize=1)
    def conference_organization(self):
        """
        Conference Organization
        v052 {'_': 'name', 'd': 'division'}
        Returns:
        {'name': '', 'division': ''}
        """
        return self.get_field_content(
            "v052", {"_": "name", "d": "division"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def conferences(self):
        """
        Conference
        v053 {'_': 'name', 'n': 'number'}
        Returns:
        {'name': '', 'number': ''}
        """
        return self.get_field_content(
            "v053", {"_": "name", "n": "number"}, False
        )

    @property
    @lru_cache(maxsize=1)
    def conference_date(self):
        """
        Conference Date
        v054
        """
        return self.get_field_content("v054", {}, True)

    @property
    @lru_cache(maxsize=1)
    def conference_date_iso(self):
        """
        Conference Date Iso
        v055
        """
        return self.get_field_content("v055", {}, True)

    @property
    @lru_cache(maxsize=1)
    def conference_location(self):
        """
        Conference Location
        v056 {'_': 'city', 'e': 'state'}
        Returns:
        {'city': '', 'state': ''}
        """
        return self.get_field_content(
            "v056", {"_": "city", "e": "state"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def conference_country(self):
        """
        Conference Country
        v057
        """
        return self.get_field_content("v057", {}, True)

    @property
    @lru_cache(maxsize=1)
    def project_sponsor(self):
        """
        Project Sponsor
        v058 {'_': 'name', 'd': 'division'}
        Returns:
        {'name': '', 'division': ''}
        """
        return self.get_field_content(
            "v058", {"_": "name", "d": "division"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def project_name(self):
        """
        Project Name
        v059
        """
        return self.get_field_content("v059", {}, True)

    @property
    @lru_cache(maxsize=1)
    def project_number(self):
        """
        Project Number
        v060
        """
        return self.get_field_content("v060", {}, True)

    @property
    @lru_cache(maxsize=1)
    def notes(self):
        """
        Notes
        v061
        """
        return self.get_field_content("v061", {}, False)

    @property
    @lru_cache(maxsize=1)
    def publisher_name(self):
        """
        Publisher Name
        v062
        """
        return self.get_field_content("v062", {}, True)

    @property
    @lru_cache(maxsize=1)
    def edition(self):
        """
        Edition
        v063
        """
        return self.get_field_content("v063", {}, True)

    @property
    @lru_cache(maxsize=1)
    def year(self):
        """
        Year
        v064
        """
        return self.get_field_content("v064", {}, True)

    @property
    @lru_cache(maxsize=1)
    def publication_date_iso(self):
        """
        Publication Date Iso
        v065
        """
        return self.get_field_content("v065", {}, True)

    @property
    @lru_cache(maxsize=1)
    def publisher_location(self):
        """
        Publisher Location
        v066 {'_': 'city', 'e': 'state'}
        Returns:
        {'city': '', 'state': ''}
        """
        return self.get_field_content(
            "v066", {"_": "city", "e": "state"}, True
        )

    @property
    @lru_cache(maxsize=1)
    def publisher_country(self):
        """
        Publisher Country
        v067
        """
        return self.get_field_content("v067", {}, True)

    @property
    @lru_cache(maxsize=1)
    def isbn(self):
        """
        ISBN
        v069
        """
        return self.get_field_content("v069", {}, True)

    @property
    @lru_cache(maxsize=1)
    def publication_type(self):
        """
        Publication Type
        v071
        """
        return self.get_field_content("v071", {}, True)

    @property
    @lru_cache(maxsize=1)
    def version(self):
        """
        Version
        v095
        """
        return self.get_field_content("v095", {}, True)

    @property
    @lru_cache(maxsize=1)
    def access_date(self):
        """
        Access date
        v109
        """
        return self.get_field_content("v109", {}, True)

    @property
    @lru_cache(maxsize=1)
    def access_date_iso(self):
        """
        Access date_iso
        v110
        """
        return self.get_field_content("v110", {}, True)

    @property
    @lru_cache(maxsize=1)
    def label(self):
        """
        Label
        v118
        """
        return self.get_field_content("v118", {}, True)

    @property
    @lru_cache(maxsize=1)
    def patent(self):
        """
        Patent
        v150 {'_': 'country', 'a': 'id', 'b': 'date', 'c': 'date_iso', 'd': 'organization'}
        Returns:
        {'country': '', 'id': '', 'date': '', 'date_iso': '', 'organization': ''}
        """
        return self.get_field_content(
            "v150",
            {
                "_": "country",
                "a": "id",
                "b": "date",
                "c": "date_iso",
                "d": "organization",
            },
            True,
        )

    @property
    @lru_cache(maxsize=1)
    def doi(self):
        """
        Doi
        v237
        """
        return self.get_field_content("v237", {}, True)

    @property
    @lru_cache(maxsize=1)
    def pmid(self):
        """
        Pmid
        v238
        """
        return self.get_field_content("v238", {}, True)

    @property
    @lru_cache(maxsize=1)
    def pmcid(self):
        """
        Pmcid
        v239
        """
        return self.get_field_content("v239", {}, True)

    @property
    @lru_cache(maxsize=1)
    def pages(self):
        """
        v514 {'e': 'elocation', 'f': 'first', 'l': 'last', 'r': 'range'}
        Returns:
        {'elocation': '', 'first': '', 'last': '', 'range': ''}
        """
        return self.get_field_content(
            "v514",
            {"e": "elocation", "f": "first", "l": "last", "r": "range"},
            False,
        )

    @property
    @lru_cache(maxsize=1)
    def index_number(self):
        """
        Index number
        v701
        """
        return self.get_field_content("v701", {}, True)

    @property
    @lru_cache(maxsize=1)
    def paragraph_text(self):
        """
        Paragraph text
        v704 {'_': ''}
        Returns:
        {'': ''}
        """
        return self.get_field_content("v704", {"_": ""}, True)

    @property
    @lru_cache(maxsize=1)
    def etal(self):
        """
        Etal
        v810
        """
        return self.get_field_content("v810", {}, True)
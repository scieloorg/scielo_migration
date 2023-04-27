from scielo_classic_website.isisdb.journal_record import JournalRecord
from scielo_classic_website.isisdb.meta_record import MetaRecord


class Journal:
    def __init__(self, journal_record):
        self.journal_record = JournalRecord(journal_record)

    def __getattr__(self, name):
        # desta forma Journal não precisa herdar de JournalRecord
        # fica menos acoplado
        if hasattr(self.journal_record, name):
            return getattr(self.journal_record, name)
        raise AttributeError(
            f"classic_website.Journal has no attribute {name}")

    @property
    def record(self):
        return self.journal_record

    @property
    def acronym(self):
        return self.journal_record.lower()

    @property
    def raw_publisher_names(self):
        return self.journal_record.publisher_name

    def get_publisher_names(self, sep="; "):
        return sep.join(self.raw_publisher_names)

    def get_publisher_loc(self, sep=", "):
        loc = [item
               for item in [self.publisher_city, self.publisher_state]
               if item]
        return sep.join(loc)

    @property
    def isis_created_date(self):
        return self.journal_record.creation_date

    @property
    def isis_updated_date(self):
        return self.journal_record.update_date

    @property
    def subject_categories(self):
        return self.journal_record.wos_subject_areas

    @property
    def study_areas(self):
        return self.journal_record.subject_areas

    @property
    def online_submission_url(self):
        return self.journal_record.submission_url

    @property
    def publication_status(self):
        return self.journal_record.current_status

    @property
    def index_at(self):
        return self.journal_record.index_coverage

    @property
    def status_history(self):
        """
        subfield a: initial date, ISO format
        subfield b: status which value is C
        subfield c: final date, ISO format
        subfield d: status which value is D or S
        v051 {'a': 'in_date', 'b': 'in_status', 'c': 'out_date', 'd': 'out_status'}
        """
        for item in self.journal_record.status_history:
            if item.get("in_status"):
                yield {
                    "date": item.get("in_date"),
                    "status": item.get("in_status"),
                }
            if item.get("out_date"):
                yield {
                    "date": item.get("out_date"),
                    "status": item.get("out_status"),
                    "reason": item.get("e"),
                }

    @property
    def unpublish_reason(self):
        _hist = sorted([
            (item.get("date"), item.get("status"))
            for item in self.status_history
        ])
        return _hist[-1][1] if _hist[-1][1] != 'C' else None

    @property
    def attributes(self):
        return dict(
            abbreviated_iso_title=self.abbreviated_iso_title,
            abbreviated_title=self.abbreviated_title,
            abstract_languages=self.abstract_languages,
            acronym=self.acronym,
            any_issn=self.any_issn,
            cnn_code=self.cnn_code,
            collection_acronym=self.collection_acronym,
            controlled_vocabulary=self.controlled_vocabulary,
            copyright_holder=self.copyright_holder,
            creation_date=self.creation_date,
            current_status=self.current_status,
            editorial_standard=self.editorial_standard,
            first_number=self.first_number,
            first_volume=self.first_volume,
            first_year=self.first_year,
            fulltitle=self.fulltitle,
            index_at=self.index_at,
            index_coverage=self.index_coverage,
            institutional_url=self.institutional_url,
            is_indexed_in_ahci=self.is_indexed_in_ahci,
            is_indexed_in_scie=self.is_indexed_in_scie,
            is_indexed_in_ssci=self.is_indexed_in_ssci,
            is_publishing_model_continuous=self.is_publishing_model_continuous,
            isis_created_date=self.isis_created_date,
            isis_updated_date=self.isis_updated_date,
            issns=self.issns,
            languages=self.languages,
            last_number=self.last_number,
            last_volume=self.last_volume,
            last_year=self.last_year,
            mission=self.mission,
            next_title=self.next_title,
            online_submission_url=self.online_submission_url,
            other_titles=self.other_titles,
            parallel_titles=self.parallel_titles,
            periodicity=self.periodicity,
            periodicity_in_months=self.periodicity_in_months,
            permissions=self.permissions,
            previous_title=self.previous_title,
            processing_date=self.processing_date,
            publication_level=self.publication_level,
            publication_status=self.publication_status,
            publisher_address=self.publisher_address,
            publisher_city=self.publisher_city,
            publisher_country=self.publisher_country,
            publisher_email=self.publisher_email,
            publisher_loc=self.publisher_loc,
            publisher_name=self.publisher_name,
            publisher_state=self.publisher_state,
            publishing_model=self.publishing_model,
            raw_publisher_names=self.raw_publisher_names,
            record=self.record,
            scielo_domain=self.scielo_domain,
            scielo_issn=self.scielo_issn,
            scimago_code=self.scimago_code,
            secs_code=self.secs_code,
            sponsors=self.sponsors,
            status_history=self.status_history,
            study_areas=self.study_areas,
            subject_areas=self.subject_areas,
            subject_categories=self.subject_categories,
            subject_descriptors=self.subject_descriptors,
            submission_url=self.submission_url,
            subtitle=self.subtitle,
            title=self.title,
            title_nlm=self.title_nlm,
            unpublish_reason=self.unpublish_reason,
            update_date=self.update_date,
            url=self.url,
            wos_citation_indexes=self.wos_citation_indexes,
            wos_subject_areas=self.wos_subject_areas,
            copyrighter=self.copyrighter,
            editor_email=self.editor_email,
            eletronic_issn=self.eletronic_issn,
            short_title=self.short_title,
            title_iso=self.title_iso,
        )

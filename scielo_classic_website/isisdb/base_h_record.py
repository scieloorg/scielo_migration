# generated by ModelBuilder
from scielo_classic_website.isisdb.meta_record import MetaRecord


ATTRIBUTES = (
    'fulltexts',
    'html_url',
    'is_ahead_of_print',
    'issue',
    'issue_label',
    'issue_url',
    'journal',
    'mixed_affiliations',
    'pdf_url',
    'translated_htmls',
    'assets_code',
    'authors',
    'corporative_authors',
    'article_titles',
    'page',
    'volume',
    'issue_number',
    'journal_id',
    'illustrative_material',
    'original_language',
    'original_section',
    'section',
    'section_code',
    'translated_section',
    'thesis_degree',
    'thesis_organization',
    'project_sponsor',
    'project_name',
    'contract',
    'issue_publication_date',
    'publication_date',
    'affiliations',
    'article_type',
    'document_type',
    'abstracts',
    'keywords',
    'processing_date',
    'update_date',
    'creation_date',
    'receive_date_iso',
    'acceptance_date_iso',
    'review_date_iso',
    'data_model_version',
    'internal_sequence_id',
    'order',
    'vol_suppl',
    'num_suppl',
    'ahead_publication_date',
    'document_publication_date',
    'doi',
    'normalized_affiliations',
    'doi_with_lang',
    'any_issn',
    'permissions',
    'languages',
    'xml_languages',
    'scielo_domain',
    'file_code',
    'original_html',
    'publisher_id',
    'scielo_pid_v2',
    'publisher_ahead_id',
    'aop_pid',
    'scielo_pid_v3',
    'collection_acronym',

)


def adapt_data(original):
    data = {}
    data['fulltexts'] = original['fulltexts']
    data['html_url'] = original['html_url']
    data['is_ahead_of_print'] = original['is_ahead_of_print']
    data['issue'] = original['issue']
    data['issue_label'] = original['issue_label']
    data['issue_url'] = original['issue_url']
    data['journal'] = original['journal']
    data['mixed_affiliations'] = original['mixed_affiliations']
    data['pdf_url'] = original['pdf_url']
    data['translated_htmls'] = original['translated_htmls']
    data['assets_code'] = original['assets_code']
    data['authors'] = original['authors']
    data['corporative_authors'] = original['corporative_authors']
    data['article_titles'] = original['article_titles']
    data['page'] = original['page']
    data['volume'] = original['volume']
    data['issue_number'] = original['issue_number']
    data['journal_id'] = original['journal_id']
    data['illustrative_material'] = original['illustrative_material']
    data['original_language'] = original['original_language']
    data['original_section'] = original['original_section']
    data['section'] = original['section']
    data['section_code'] = original['section_code']
    data['translated_section'] = original['translated_section']
    data['thesis_degree'] = original['thesis_degree']
    data['thesis_organization'] = original['thesis_organization']
    data['project_sponsor'] = original['project_sponsor']
    data['project_name'] = original['project_name']
    data['contract'] = original['contract']
    data['issue_publication_date'] = original['issue_publication_date']
    data['publication_date'] = original['publication_date']
    data['affiliations'] = original['affiliations']
    data['article_type'] = original['article_type']
    data['document_type'] = original['document_type']
    data['abstracts'] = original['abstracts']
    data['keywords'] = original['keywords']
    data['processing_date'] = original['processing_date']
    data['update_date'] = original['update_date']
    data['creation_date'] = original['creation_date']
    data['receive_date_iso'] = original['receive_date_iso']
    data['acceptance_date_iso'] = original['acceptance_date_iso']
    data['review_date_iso'] = original['review_date_iso']
    data['data_model_version'] = original['data_model_version']
    data['internal_sequence_id'] = original['internal_sequence_id']
    data['order'] = original['order']
    data['vol_suppl'] = original['vol_suppl']
    data['num_suppl'] = original['num_suppl']
    data['ahead_publication_date'] = original['ahead_publication_date']
    data['document_publication_date'] = original['document_publication_date']
    data['doi'] = original['doi']
    data['normalized_affiliations'] = original['normalized_affiliations']
    data['doi_with_lang'] = original['doi_with_lang']
    data['any_issn'] = original['any_issn']
    data['permissions'] = original['permissions']
    data['languages'] = original['languages']
    data['xml_languages'] = original['xml_languages']
    data['scielo_domain'] = original['scielo_domain']
    data['file_code'] = original['file_code']
    data['original_html'] = original['original_html']
    data['publisher_id'] = original['publisher_id']
    data['scielo_pid_v2'] = original['scielo_pid_v2']
    data['publisher_ahead_id'] = original['publisher_ahead_id']
    data['aop_pid'] = original['aop_pid']
    data['scielo_pid_v3'] = original['scielo_pid_v3']
    data['collection_acronym'] = original['collection_acronym']
    return data


# generated by ModelBuilder
class BaseDocumentRecord(MetaRecord):

    def __init__(
            self, record, multi_val_tags=None,
            data_dictionary=None):
        super().__init__(
            record, multi_val_tags, data_dictionary)

    # generated by ModelBuilder
    @property
    def attributes(self):
        return dict(
            [(k, getattr(self, k)) for k in ATTRIBUTES]
        )

    # generated by ModelBuilder
    @property
    def text_languages(self):
        """
        Fulltexts languages
        v601
        """
        return self.get_field_content("v601", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def html_url(self):
        """
        Html Url
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def is_ahead_of_print(self):
        """
        Is Ahead Of Print
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def issue(self):
        """
        Issue
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def issue_label(self):
        """
        Issue Label
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def issue_url(self):
        """
        Issue Url
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def journal(self):
        """
        Journal
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def mixed_affiliations(self):
        """
        Mixed Affiliations
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def pdf_url(self):
        """
        Pdf Url
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def translated_htmls(self):
        """
        Translated Htmls
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def assets_code(self):
        """
        Assets Code
        v004
        """
        return self.get_field_content("v004", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def authors(self):
        """
        Author
        v010 {'1': 'xref', 'k': 'orcid', 'l': 'lattes', 'n': 'given_names', 'p': 'prefix', 'r': 'role', 's': 'surname'}
        """
        return self.get_field_content("v010", subfields={'1': 'xref', 'k': 'orcid', 'l': 'lattes', 'n': 'given_names', 'p': 'prefix', 'r': 'role', 's': 'surname'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def corporative_authors(self):
        """
        Corporative Authors
        v011
        """
        return self.get_field_content("v011", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def article_titles(self):
        """
        Article Titles
        v012 {'s': 'subtitle', '_': 'text', 'l': 'language'}
        """
        return self.get_field_content("v012", subfields={'s': 'subtitle', '_': 'text', 'l': 'language'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def page(self):
        """
        Page
        v014 {'e': 'elocation', 'f': 'start', 'l': 'end', 's': 'sequence'}
        """
        return self.get_field_content("v014", subfields={'e': 'elocation', 'f': 'start', 'l': 'end', 's': 'sequence'}, single=True, simple=False)

    # generated by ModelBuilder
    @property
    def volume(self):
        """
        Volume
        v031
        """
        return self.get_field_content("v031", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def issue_number(self):
        """
        Number
        v032
        """
        return self.get_field_content("v032", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def journal_id(self):
        """
        Journal ID
        v035
        """
        return self.get_field_content("v035", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def illustrative_material(self):
        """
        Illustrative Material
        v038
        """
        return self.get_field_content("v038", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def original_language(self):
        """
        Original Language
        v040
        """
        return self.get_field_content("v040", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def original_section(self):
        """
        Original Section
        v049
        """
        return self.get_field_content("v049", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def section(self):
        """
        Section
        v049
        """
        return self.get_field_content("v049", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def section_code(self):
        """
        Section Code
        v049
        """
        return self.get_field_content("v049", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def translated_section(self):
        """
        Translated Section
        v049
        """
        return self.get_field_content("v049", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def thesis_degree(self):
        """
        Thesis Degree
        v051
        """
        return self.get_field_content("v051", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def thesis_organization(self):
        """
        Thesis Organization
        v052
        """
        return self.get_field_content("v052", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def project_sponsor(self):
        """
        Project Sponsor
        v058
        """
        return self.get_field_content("v058", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def project_name(self):
        """
        Project Name
        v059
        """
        return self.get_field_content("v059", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def contract(self):
        """
        Contract
        v060
        """
        return self.get_field_content("v060", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def issue_publication_date(self):
        """
        Issue Publication Date
        v065
        """
        return self.get_field_content("v065", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publication_date(self):
        """
        Publication Date
        v065
        """
        return self.get_field_content("v065", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def affiliations(self):
        """
        Affiliations
        v070 {'d': 'div1', '1': 'div1', '2': 'div2', '3': 'div3', 'o': 'orgname', '_': 'orgname', 'c': 'city', 'e': 'email', 'i': 'id', 'p': 'country', 's': 'state'}
        """
        return self.get_field_content("v070", subfields={'d': 'div1', '1': 'div1', '2': 'div2', '3': 'div3', 'o': 'orgname', '_': 'orgname', 'c': 'city', 'e': 'email', 'i': 'id', 'p': 'country', 's': 'state'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def article_type(self):
        """
        Article Type
        v071
        """
        return self.get_field_content("v071", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def document_type(self):
        """
        Document Type
        v071
        """
        return self.get_field_content("v071", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def abstracts(self):
        """
        Abstracts
        v083 {'_': 'text', 'a': 'text', 'l': 'language'}
        """
        return self.get_field_content("v083", subfields={'_': 'text', 'a': 'text', 'l': 'language'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def keywords(self):
        """
        Keywords
        v085 {'k': 'text', 's': 'subkey', 'l': 'language'}
        """
        return self.get_field_content("v085", subfields={'k': 'text', 's': 'subkey', 'l': 'language'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def processing_date(self):
        """
        Processing Date
        v091
        """
        return self.get_field_content("v091", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def update_date(self):
        """
        Update Date
        v091
        """
        return self.get_field_content("v091", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def creation_date(self):
        """
        Creation Date
        v093
        """
        return self.get_field_content("v093", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def receive_date_iso(self):
        """
        Receive Date ISO
        v112
        """
        return self.get_field_content("v112", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def acceptance_date_iso(self):
        """
        Acceptance Date ISO
        v114
        """
        return self.get_field_content("v114", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def review_date_iso(self):
        """
        Review Date ISO
        v116
        """
        return self.get_field_content("v116", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def data_model_version(self):
        """
        Data Model Version
        v120
        """
        return self.get_field_content("v120", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def internal_sequence_id(self):
        """
        Internal Sequence Id
        v121
        """
        return self.get_field_content("v121", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def order(self):
        """
        Order
        v121
        """
        return self.get_field_content("v121", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def vol_suppl(self):
        """
        Supplement
        v131
        """
        return self.get_field_content("v131", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def num_suppl(self):
        """
        Supplement
        v132
        """
        return self.get_field_content("v132", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def ahead_publication_date(self):
        """
        Ahead Publication Date
        v223
        """
        return self.get_field_content("v223", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def document_publication_date(self):
        """
        Document Publication Date
        v223
        """
        return self.get_field_content("v223", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def doi(self):
        """
        DOI
        v237
        """
        return self.get_field_content("v237", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def normalized_affiliations(self):
        """
        Normalized Affiliations
        v240 {'i': 'id', 'p': 'country'}
        """
        return self.get_field_content("v240", subfields={'i': 'id', 'p': 'country'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def doi_with_lang(self):
        """
        DOI with language
        v337 {'d': 'doi', 'l': 'language'}
        """
        return self.get_field_content("v337", subfields={'d': 'doi', 'l': 'language'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def any_issn(self):
        """
        Any Issn
        v435 {'_': 'value', 't': 'type'}
        """
        return self.get_field_content("v435", subfields={'_': 'value', 't': 'type'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def permissions(self):
        """
        Permissions
        v540
        """
        return self.get_field_content("v540", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def languages(self):
        """
        Languages
        v601
        """
        return self.get_field_content("v601", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def xml_languages(self):
        """
        Xml Languages
        v601
        """
        return self.get_field_content("v601", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def scielo_domain(self):
        """
        Scielo Domain
        v690
        """
        return self.get_field_content("v690", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def file_code(self):
        """
        File Code
        v702
        """
        return self.get_field_content("v702", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def original_html(self):
        """
        Original Html
        v702
        """
        return self.get_field_content("v702", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publisher_id(self):
        """
        Publisher Id
        v880
        """
        return self.get_field_content("v880", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def scielo_pid_v2(self):
        """
        SciELO PID v2
        v880
        """
        return self.get_field_content("v880", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publisher_ahead_id(self):
        """
        Publisher Ahead Id
        v881
        """
        return self.get_field_content("v881", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def aop_pid(self):
        """
        Ahead Of Print Id
        v881
        """
        return self.get_field_content("v881", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def scielo_pid_v3(self):
        """
        SciELO PID v3
        v885
        """
        return self.get_field_content("v885", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def collection_acronym(self):
        """
        Collection Acronym
        v992
        """
        return self.get_field_content("v992", subfields={}, single=True, simple=True)


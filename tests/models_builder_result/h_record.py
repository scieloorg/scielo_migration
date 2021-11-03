from scielo_migratin.iid2json.meta_record import MetaRecord


class H_Record(MetaRecord):

    def __init__(
            self, record, no_repetition_tags=None, no_subfield_tags=None,
            data_dictionary=None):
        super().__init__(
            record, no_repetition_tags, no_subfield_tags, data_dictionary)

    @property
    def ccode(self):
        """
        ccode

        v001
        """
        return self.get_field_content("v001")

    @property
    def authgrp_author(self):
        """
        authgrp_author

        v010 {'n': 'given_names', '1': 'rid', 'r': 'role', 's': 'surname'}
        """
        return self.get_field_content(
            "v010",
            subfields={'n': 'given_names', '1': 'rid', 'r': 'role', 's': 'surname'})

    @property
    def authgrp_corpauth(self):
        """
        authgrp_corpauth

        v011 {'d': 'orgdiv', '_': 'orgname'}
        """
        return self.get_field_content(
            "v011",
            subfields={'d': 'orgdiv', '_': 'orgname'})

    @property
    def history_received(self):
        """
        history_received

        v111
        """
        return self.get_field_content("v111")

    @property
    def history_received_dateiso(self):
        """
        history_received_dateiso

        v112
        """
        return self.get_field_content("v112")

    @property
    def history_accepted(self):
        """
        history_accepted

        v113
        """
        return self.get_field_content("v113")

    @property
    def history_accepted_dateiso(self):
        """
        history_accepted_dateiso

        v114
        """
        return self.get_field_content("v114")

    @property
    def history_revised(self):
        """
        history_revised

        v115
        """
        return self.get_field_content("v115")

    @property
    def history_revised_dateiso(self):
        """
        history_revised_dateiso

        v116
        """
        return self.get_field_content("v116")

    @property
    def biblist_head_standard(self):
        """
        biblist_head_standard

        v117
        """
        return self.get_field_content("v117")

    @property
    def title(self):
        """
        title

        v012 {'l': 'language', '_': 'title'}
        """
        return self.get_field_content(
            "v012",
            subfields={'l': 'language', '_': 'title'})

    @property
    def version(self):
        """
        version

        v120
        """
        return self.get_field_content("v120")

    @property
    def order(self):
        """
        order

        v121
        """
        return self.get_field_content("v121")

    @property
    def toccode(self):
        """
        toccode

        v123
        """
        return self.get_field_content("v123")

    @property
    def supplvol(self):
        """
        supplvol

        v131
        """
        return self.get_field_content("v131")

    @property
    def supplno(self):
        """
        supplno

        v132
        """
        return self.get_field_content("v132")

    @property
    def figgrp(self):
        """
        figgrp

        v141 {'r': 'figref', 'm': 'legend', 'n': 'no', 's': 'subtitle', 't': 'title', 'l': 'language'}
        """
        return self.get_field_content(
            "v141",
            subfields={'r': 'figref', 'm': 'legend', 'n': 'no', 's': 'subtitle', 't': 'title', 'l': 'language'})

    @property
    def table(self):
        """
        table

        v142 {'m': 'legend', 'n': 'no', 's': 'subtitle', 't': 'title', 'l': 'language'}
        """
        return self.get_field_content(
            "v142",
            subfields={'m': 'legend', 'n': 'no', 's': 'subtitle', 't': 'title', 'l': 'language'})

    @property
    def sponsor(self):
        """
        sponsor

        v158
        """
        return self.get_field_content("v158")

    @property
    def pii(self):
        """
        pii

        v002
        """
        return self.get_field_content("v002")

    @property
    def ahpdate(self):
        """
        ahpdate

        v223
        """
        return self.get_field_content("v223")

    @property
    def rvpdate(self):
        """
        rvpdate

        v224
        """
        return self.get_field_content("v224")

    @property
    def old_pid(self):
        """
        old_pid

        v225
        """
        return self.get_field_content("v225")

    @property
    def doi(self):
        """
        doi

        v237
        """
        return self.get_field_content("v237")

    @property
    def url(self):
        """
        url

        v238
        """
        return self.get_field_content("v238")

    @property
    def product(self):
        """
        product

        v241 {'t': 'reltype', 'i': 'relid', 'z': 'relidtp'}
        """
        return self.get_field_content(
            "v241",
            subfields={'t': 'reltype', 'i': 'relid', 'z': 'relidtp'})

    @property
    def hcomment(self):
        """
        hcomment

        v250
        """
        return self.get_field_content("v250")

    @property
    def deposit_embdate(self):
        """
        deposit_embdate

        v264
        """
        return self.get_field_content("v264")

    @property
    def deposit_entrdate(self):
        """
        deposit_entrdate

        v265
        """
        return self.get_field_content("v265")

    @property
    def deposit_deposid(self):
        """
        deposit_deposid

        v268
        """
        return self.get_field_content("v268")

    @property
    def issuegrp_volid(self):
        """
        issuegrp_volid

        v031
        """
        return self.get_field_content("v031")

    @property
    def issuegrp_issueno(self):
        """
        issuegrp_issueno

        v032
        """
        return self.get_field_content("v032")

    @property
    def issn(self):
        """
        issn

        v035
        """
        return self.get_field_content("v035")

    @property
    def type(self):
        """
        type

        v038
        """
        return self.get_field_content("v038")

    @property
    def language(self):
        """
        language

        v040
        """
        return self.get_field_content("v040")

    @property
    def isidpart(self):
        """
        isidpart

        v041
        """
        return self.get_field_content("v041")

    @property
    def status(self):
        """
        status

        v042
        """
        return self.get_field_content("v042")

    @property
    def thesis_date(self):
        """
        thesis_date

        v044
        """
        return self.get_field_content("v044")

    @property
    def thesis_date_dateiso(self):
        """
        thesis_date_dateiso

        v045
        """
        return self.get_field_content("v045")

    @property
    def thesis(self):
        """
        thesis

        v046 {'e': 'state', '_': 'city'}
        """
        return self.get_field_content(
            "v046",
            subfields={'e': 'state', '_': 'city'})

    @property
    def thesis_country(self):
        """
        thesis_country

        v047
        """
        return self.get_field_content("v047")

    @property
    def seccode(self):
        """
        seccode

        v049
        """
        return self.get_field_content("v049")

    @property
    def thesis(self):
        """
        thesis

        v050 {'d': 'orgdiv', '_': 'orgname'}
        """
        return self.get_field_content(
            "v050",
            subfields={'d': 'orgdiv', '_': 'orgname'})

    @property
    def thesis_degree(self):
        """
        thesis_degree

        v051
        """
        return self.get_field_content("v051")

    @property
    def conference_sponsor(self):
        """
        conference_sponsor

        v052 {'d': 'orgdiv', '_': 'orgname'}
        """
        return self.get_field_content(
            "v052",
            subfields={'d': 'orgdiv', '_': 'orgname'})

    @property
    def conference(self):
        """
        conference

        v053 {'n': 'no'}
        """
        return self.get_field_content(
            "v053",
            subfields={'n': 'no'})

    @property
    def conference_date(self):
        """
        conference_date

        v054 {'_': 'date'}
        """
        return self.get_field_content(
            "v054",
            subfields={'_': 'date'})

    @property
    def license(self):
        """
        license

        v540 {'u': 'href', 'l': 'language', 't': 'lictype', '_': 'licensep'}
        """
        return self.get_field_content(
            "v540",
            subfields={'u': 'href', 'l': 'language', 't': 'lictype', '_': 'licensep'})

    @property
    def conference_date_dateiso(self):
        """
        conference_date_dateiso

        v055 {'_': 'dateiso'}
        """
        return self.get_field_content(
            "v055",
            subfields={'_': 'dateiso'})

    @property
    def conference(self):
        """
        conference

        v056 {'e': 'state', '_': 'city'}
        """
        return self.get_field_content(
            "v056",
            subfields={'e': 'state', '_': 'city'})

    @property
    def conference_country(self):
        """
        conference_country

        v057 {'_': 'country'}
        """
        return self.get_field_content(
            "v057",
            subfields={'_': 'country'})

    @property
    def projgrp_psponsor(self):
        """
        projgrp_psponsor

        v058 {'d': 'orgdiv', '_': 'orgname'}
        """
        return self.get_field_content(
            "v058",
            subfields={'d': 'orgdiv', '_': 'orgname'})

    @property
    def projgrp_projname(self):
        """
        projgrp_projname

        v059
        """
        return self.get_field_content("v059")

    @property
    def report_awarded(self):
        """
        report_awarded

        v591 {'n': 'given_names', 'd': 'orgdiv', 's': 'surname', '_': 'orgname'}
        """
        return self.get_field_content(
            "v591",
            subfields={'n': 'given_names', 'd': 'orgdiv', 's': 'surname', '_': 'orgname'})

    @property
    def report_no(self):
        """
        report_no

        v592
        """
        return self.get_field_content("v592")

    @property
    def projgrp_psponsor_contract(self):
        """
        projgrp_psponsor_contract

        v060
        """
        return self.get_field_content("v060")

    @property
    def issuegrp_date(self):
        """
        issuegrp_date

        v064
        """
        return self.get_field_content("v064")

    @property
    def dateiso(self):
        """
        dateiso

        v065
        """
        return self.get_field_content("v065")

    @property
    def aff(self):
        """
        aff

        v070 {'c': 'city', 'p': 'country', 'e': 'email', 'i': 'id', '1': 'orgdiv1', '2': 'orgdiv2', '3': 'orgdiv3', 'd': 'orgdiv', 's': 'state', 'z': 'zipcode', '_': 'orgname'}
        """
        return self.get_field_content(
            "v070",
            subfields={'c': 'city', 'p': 'country', 'e': 'email', 'i': 'id', '1': 'orgdiv1', '2': 'orgdiv2', '3': 'orgdiv3', 'd': 'orgdiv', 's': 'state', 'z': 'zipcode', '_': 'orgname'})

    @property
    def doctopic(self):
        """
        doctopic

        v071
        """
        return self.get_field_content("v071")

    @property
    def biblist_head_count(self):
        """
        biblist_head_count

        v072
        """
        return self.get_field_content("v072")

    @property
    def keygrp_dperiod(self):
        """
        keygrp_dperiod

        v074 {'f': 'from', 't': 'to'}
        """
        return self.get_field_content(
            "v074",
            subfields={'f': 'from', 't': 'to'})

    @property
    def cltrial(self):
        """
        cltrial

        v770 {'a': 'ctreg', 'u': 'cturl', '_': 'ctdbid'}
        """
        return self.get_field_content(
            "v770",
            subfields={'a': 'ctreg', 'u': 'cturl', '_': 'ctdbid'})

    @property
    def v083(self):
        """
        v083

        v083 {'a': 'abstract', 'l': 'language'}
        """
        return self.get_field_content(
            "v083",
            subfields={'a': 'abstract', 'l': 'language'})

    @property
    def keygrp(self):
        """
        keygrp

        v085 {'k': 'keyword', 'd': 'scheme', 's': 'subkey', 'l': 'language', 't': 'type', '_': 'rid'}
        """
        return self.get_field_content(
            "v085",
            subfields={'k': 'keyword', 'd': 'scheme', 's': 'subkey', 'l': 'language', 't': 'type', '_': 'rid'})

    @property
    def fpage(self):
        """
        fpage

        v914
        """
        return self.get_field_content("v914")

    @property
    def lpage(self):
        """
        lpage

        v915
        """
        return self.get_field_content("v915")


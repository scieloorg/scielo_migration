import logging
from datetime import datetime
from io import StringIO

import plumber
from lxml import etree as ET

from scielo_classic_website.htmlbody.html_code_utils import html_decode

from . import utils, xylose_adapters


def parse_yyyymmdd(yyyymmdd):
    """
    Get year, month and day from date format which MM and DD can be 00
    """
    year, month, day = None, None, None
    try:
        _year = int(yyyymmdd[:4])
        d = datetime(_year, 1, 1)
        year = _year

        _month = int(yyyymmdd[4:6])
        d = datetime(year, _month, 1)
        month = _month

        _day = int(yyyymmdd[6:])
        d = datetime(year, month, _day)
        day = _day

    except:
        pass

    return year, month, day


def iso_8601_date(yyyymmdd):
    parsed_yyyymmdd = parse_yyyymmdd(yyyymmdd)
    return "-".join([item for item in list(parsed_yyyymmdd) if item])


class XMLArticleMetaCitationsPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data
        if not list(raw.citations):
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        article = xml.find(".")
        back = article.find("back")
        if back is None:
            back = ET.Element("back")
            article.append(back)

        reflist = xml.find("./back/ref-list")
        if reflist is None:
            reflist = ET.Element("ref-list")
            back.append(reflist)

        refs = ET.Element("ref-list")

        cit = XMLCitation()
        for i, citation in enumerate(raw.citations):
            try:
                citation.fix_function = html_decode
                ref = cit.deploy(xylose_adapters.ReferenceXyloseAdapter(citation))[1]
                if ref is not None:
                    if ref.find(".//mixed-citation") is None:
                        ref_id = ref.get("id")
                        r = reflist.find(f".//ref[@id='{ref_id}']")
                        if r is not None:
                            mixed_citation = r.find(".//mixed-citation")
                            if mixed_citation is not None:
                                ref.insert(0, mixed_citation)
                    refs.append(ref)
            except Exception as e:
                logging.info(i)
                logging.exception(e)
                raise e
        back.replace(reflist, refs)
        return data


class XMLCitation(object):
    def __init__(self):
        self._ppl = plumber.Pipeline(
            self.SetupCitationPipe(),
            self.RefIdPipe(),
            self.MixedCitationPipe(),
            self.ElementCitationPipe(),
            self.PersonGroupPipe(),
            self.ArticleTitlePipe(),
            self.ChapterTitlePipe(),
            self.DataTitlePipe(),
            self.SourcePipe(),
            self.ConferencePipe(),
            self.ThesisPipe(),
            self.PatentPipe(),
            self.VolumePipe(),
            self.IssuePipe(),
            self.SupplementPipe(),
            self.IssuePartPipe(),
            self.IssueTitlePipe(),
            self.ElocationIdPipe(),
            self.PageRangePipe(),
            self.SizePipe(),
            self.StartPagePipe(),
            self.EndPagePipe(),
            self.IssnPipe(),
            self.PubIdPipe(),
            self.DatePipe(),
            self.EditionPipe(),
            self.IsbnPipe(),
            self.VersionPipe(),
            self.SeriesPipe(),
            self.DateInCitatioPipe(),
            self.LinkPipe(),
            self.CommentPipe(),
            self.ProjectPipe(),
        )

    class SetupCitationPipe(plumber.Pipe):
        def transform(self, data):
            xml = ET.Element("ref")
            return data, xml

    class RefIdPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            ref = xml.find(".")

            ref.set("id", "B{0}".format(str(raw.index_number)))

            return data

    class MixedCitationPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data
            mixed_citation = raw.mixed_citation
            if mixed_citation is not None:
                logging.info("mixed_citation %s" % mixed_citation)
                xml.append(utils.convert_all_html_tags_to_jats(mixed_citation))

            return data

    class ElementCitationPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            elementcitation = ET.Element("element-citation")
            elementcitation.set("publication-type", raw.publication_type or "other")

            xml.find(".").append(elementcitation)

            return data

    class ArticleTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.article_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data
            logging.info(type(raw))
            articletitle = ET.Element("article-title")

            articletitle.text = raw.article_title

            xml.find("./element-citation").append(articletitle)

            return data

    class ChapterTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.chapter_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            articletitle = ET.Element("chapter-title")

            articletitle.text = raw.chapter_title

            xml.find("./element-citation").append(articletitle)

            return data

    class DataTitlePipe(plumber.Pipe):
        """
        https://jats.nlm.nih.gov/publishing/tag-library/1.3/element/data-title.html
        """

        def precond(data):
            raw, xml = data

            if not raw.data_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            articletitle = ET.Element("data-title")

            articletitle.text = raw.data_title

            xml.find("./element-citation").append(articletitle)

            return data

    class SourcePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.source:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            source = ET.Element("source")

            source.text = raw.source

            xml.find("./element-citation").append(source)

            return data

    class CommentPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            if raw.comment and not raw.link:
                comment = ET.Element("comment")
                comment.text = raw.comment
                xml.find("./element-citation").append(comment)

            return data

    class ProjectPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            if raw.project_name:
                comment = ET.Element("comment")
                comment.set("content-type", "project-name")
                comment.text = raw.project_name
                xml.find("./element-citation").append(comment)

            if raw.project_number:
                comment = ET.Element("comment")
                comment.set("content-type", "project-number")
                comment.text = raw.project_number
                xml.find("./element-citation").append(comment)

            if raw.project_sponsor:
                comment = ET.Element("comment")
                comment.set("content-type", "project-sponsor")
                comment.text = ", ".join(
                    [item for item in raw.project_sponsor.values() if item]
                )
                xml.find("./element-citation").append(comment)

            return data

    class DatePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.publication_date:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            pdate = ET.Element("date")

            date = {
                "year": raw.publication_date[0:4],
                "month": raw.publication_date[5:7],
                "day": raw.publication_date[8:10],
            }

            for name, value in date.items():
                if value and value.isdigit() and int(value) > 0:
                    date_element = ET.Element(name)
                    date_element.text = value
                    pdate.append(date_element)

            xml.find("./element-citation").append(pdate)

            year = ET.Element("year")
            year.text = raw.publication_date[0:4]
            xml.find("./element-citation").append(year)

            return data

    class StartPagePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.start_page:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            fpage = ET.Element("fpage")
            fpage.text = raw.start_page
            xml.find("./element-citation").append(fpage)

            return data

    class EndPagePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.end_page:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            lpage = ET.Element("lpage")
            lpage.text = raw.end_page
            xml.find("./element-citation").append(lpage)

            return data

    class PageRangePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.pages_range:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elem = ET.Element("page-range")
            elem.text = raw.pages_range
            xml.find("./element-citation").append(elem)

            return data

    class SizePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.size:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elem = ET.Element("size")
            elem.set("units", raw.size.get("unit") or "pages")
            elem.text = raw.size.get("size")
            xml.find("./element-citation").append(elem)

            return data

    class IssuePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issue:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issue = ET.Element("issue")
            issue.text = raw.issue
            xml.find("./element-citation").append(issue)

            return data

    class IssuePartPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issue_part:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issue_part = ET.Element("issue-part")
            issue_part.text = raw.issue_part
            xml.find("./element-citation").append(issue_part)

            return data

    class IssueTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issue_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issue_title = ET.Element("issue-title")
            issue_title.text = raw.issue_title
            xml.find("./element-citation").append(issue_title)

            return data

    class SupplementPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.supplement:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            supplement = ET.Element("supplement")
            supplement.text = raw.supplement
            xml.find("./element-citation").append(supplement)

            return data

    class VolumePipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data
            print((raw.volume, raw.colvolid, raw.tome))
            if raw.volume or raw.colvolid or raw.tome:
                volume = ET.Element("volume")
                volume.text = raw.volume or raw.colvolid or raw.tome
                xml.find("./element-citation").append(volume)

            return data

    class EditionPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.edition:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            edition = ET.Element("edition")
            edition.text = raw.edition
            xml.find("./element-citation").append(edition)

            return data

    class SeriesPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.coltitle:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            coltitle = ET.Element("series")
            coltitle.text = raw.coltitle
            xml.find("./element-citation").append(coltitle)

            return data

    class ElocationIdPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.elocation:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elocation = ET.Element("elocation-id")
            elocation.text = raw.elocation
            xml.find("./element-citation").append(elocation)

            return data

    class VersionPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.version:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            version = ET.Element("version")
            version.text = raw.version
            xml.find("./element-citation").append(version)

            return data

    class IsbnPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.isbn:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            isbn = ET.Element("isbn")
            isbn.text = raw.isbn
            xml.find("./element-citation").append(isbn)

            return data

    class IssnPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issn:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issn = ET.Element("issn")
            issn.text = raw.issn
            xml.find("./element-citation").append(issn)

            return data

    class PatentPipe(plumber.Pipe):
        """
        <patent country="US">United States patent US 6,980,855</patent>
        """

        def precond(data):
            raw, xml = data

            if not raw.patent:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            patent = ET.Element("patent")
            if raw.patent_country:
                patent.set("country", raw.patent_country)
            text = [
                raw.patent_country,
                raw.patent_organization,
                raw.patent_id,
            ]
            patent.text = " ".join([t for t in text if t])
            xml.find("./element-citation").append(patent)

            return data

    class PersonGroupPipe(plumber.Pipe):
        def build_name(self, author):
            name = ET.Element("name")
            if author.get("surname"):
                elem = ET.Element("surname")
                elem.text = author.get("surname")
                name.append(elem)
            if author.get("given_names"):
                elem = ET.Element("given-names")
                elem.text = author.get("given_names")
                name.append(elem)
            if author.get("anonymous"):
                elem = ET.Element("anonymous")
                elem.text = author.get("given_names")
                name.append(elem)
            if name.getchildren():
                return name

        def build_person_authors(self, authors):
            if len(authors):
                group = ET.Element("person-group")
                group_type = None
                for author in authors:
                    name = self.build_name(author)
                    if name:
                        group.append(name)
                    group_type = author.get("role")
                if not group_type or group_type.lower() == "nd":
                    group_type = "authors"
                group.set("person-group-type", group_type)
                return group

        def build_collab(self, author):
            text = [author.get("name"), author.get("division")]
            text = ", ".join([item for item in text if item])
            if text:
                elem = ET.Element("collab")
                elem.text = text
                return elem

        def build_institutional_authors(self, authors):
            if len(authors):
                group = ET.Element("person-group")
                group_type = None
                for author in authors:
                    name = self.build_collab(author)
                    if name:
                        group.append(name)
                    group_type = author.get("role")
                if not group_type or group_type.lower() == "nd":
                    group_type = "authors"
                group.set("person-group-type", group_type)
                return group

        def transform(self, data):
            raw, xml = data

            citation = xml.find("./element-citation")

            person_group = self.build_person_authors(raw.analytic_person_authors)
            if person_group:
                citation.append(person_group)

            person_group = self.build_person_authors(raw.monographic_person_authors)
            if person_group:
                citation.append(person_group)

            person_group = self.build_person_authors(raw.serial_person_authors)
            if person_group:
                citation.append(person_group)

            person_group = self.build_institutional_authors(
                raw.analytic_corporative_authors
            )
            if person_group:
                citation.append(person_group)

            person_group = self.build_institutional_authors(
                raw.monographic_corporative_authors
            )
            if person_group:
                citation.append(person_group)

            person_group = self.build_institutional_authors(
                raw.serial_corporative_authors
            )
            if person_group:
                citation.append(person_group)

            if person_group and raw.etal:
                xml.find(".//person-group").append(ET.Element("etal"))
            return data

    class ConferencePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if raw.publication_type != "confproc":
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find("./element-citation")

            if raw.conference_name:
                elem = ET.Element("conf-name")
                elem.text = raw.conference_name
                elementcitation.append(elem)

            if raw.conference_date_iso:
                elem = ET.Element("conf-date")
                elem.set("iso-8601-date", iso_8601_date(raw.conference_date_iso))
                elem.text = raw.conference_date or ""
                elementcitation.append(elem)

            conf_loc = ET.Element("conf-loc")
            if raw.conference_location:
                for name in ("city", "state"):
                    data = raw.conference_location.get(name)
                    if data:
                        elem = ET.Element(name)
                        elem.text = data
                        conf_loc.append(elem)

            if raw.conference_country:
                elem = ET.Element("country")
                elem.text = raw.conference_country
                conf_loc.append(elem)
            if conf_loc.find("*") is not None:
                elementcitation.append(conf_loc)

            if raw.conference_sponsor:
                elem = ET.Element("conf-sponsor")
                elem.text = raw.conference_sponsor
                elementcitation.append(elem)

            return data

    class ThesisPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if raw.publication_type != "thesis":
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find("./element-citation")

            if raw.thesis_institution:
                elem = ET.Element("publisher-name")
                elem.text = raw.thesis_institution
                elementcitation.append(elem)

            publisher_loc = ET.Element("publisher-loc")
            if raw.thesis_location:
                for name in ("city", "state"):
                    data = raw.thesis_location.get(name)
                    if data:
                        elem = ET.Element(name)
                        elem.text = data
                        publisher_loc.append(elem)

            if raw.thesis_country:
                elem = ET.Element("country")
                elem.text = raw.thesis_country
                publisher_loc.append(elem)

            if publisher_loc.find("*") is not None:
                elementcitation.append(publisher_loc)

            if raw.thesis_degree:
                elem = ET.Element("comment")
                elem.set("content-type", "degree")
                elem.text = raw.thesis_degree
                elementcitation.append(elem)
            return data

    class PublicationPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find("./element-citation")

            if raw.publisher_name:
                elem = ET.Element("publisher-name")
                elem.text = raw.publisher_name
                elementcitation.append(elem)

            publisher_loc = ET.Element("publisher-loc")
            if raw.publisher_location:
                for name in ("city", "state"):
                    data = raw.publisher_location.get(name)
                    if data:
                        elem = ET.Element(name)
                        elem.text = data
                        publisher_loc.append(elem)

            if raw.publisher_country:
                elem = ET.Element("country")
                elem.text = raw.publisher_country
                publisher_loc.append(elem)

            if publisher_loc.find("*") is not None:
                elementcitation.append(publisher_loc)

            return data

    class LinkPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.ext_link:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data
            if raw.link and raw.comment:
                comment = ET.Element("comment")
                comment.text = raw.comment
                link = ET.Element("ext-link")
                link.set("ext-link-type", "uri")
                link.set("{http://www.w3.org/1999/xlink}href", "http://%s" % raw.link)
                link.text = raw.link
                comment.append(link)
                xml.find("./element-citation").append(comment)

            elif raw.link:
                link = ET.Element("ext-link")
                link.set("ext-link-type", "uri")
                link.set("{http://www.w3.org/1999/xlink}href", "http://%s" % raw.link)
                link.text = raw.link
                xml.find("./element-citation").append(link)
            return data

    class DateInCitatioPipe(plumber.Pipe):
        """
        A <date-in-citation> element SHOULD NOT be used to record the
        publication date; instead use the specific date elements such as
        <year> and <month> or the combination publishing date element <date>.
        The <date-in-citation> element SHOULD BE used to record
        non-publication dates such as ACCESS DATES, copyright dates,
        patent application dates, or time stamps indicating the exact
        time the work was published for a continuously or frequently updated source.
        """

        def precond(data):
            raw, xml = data

            if not raw.access_date and not raw.access_date_iso:
                raise plumber.UnmetPrecondition()

            if not raw.patent_application_date and not raw.patent_application_date_iso:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find("./element-citation")

            content_type = (
                (raw.access_date or raw.access_date_iso) and "access-date"
            ) or (
                (raw.patent_application_date or raw.patent_application_date_iso)
                and "patent-application-date"
            )
            elem = ET.Element("date-in-citation")
            elem.set("content-type", content_type)
            elem.set(
                "iso-8601-date",
                iso_8601_date(raw.access_date_iso or raw.patent_application_date_iso),
            )
            elem.text = raw.access_date or raw.patent_application_date
            elementcitation.append(elem)
            return data

    class PubIdPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find("./element-citation")

            if raw.pmid:
                elem = ET.Element("pub-id")
                elem.set("pub-id-type", "pmid")
                elem.text = raw.pmid
                elementcitation.append(elem)

            if raw.pmcid:
                elem = ET.Element("pub-id")
                elem.set("pub-id-type", "pmcid")
                elem.text = raw.pmcid
                elementcitation.append(elem)

            if raw.doi:
                elem = ET.Element("pub-id")
                elem.set("pub-id-type", "doi")
                elem.text = raw.doi
                elementcitation.append(elem)
            return data

    def deploy(self, raw):
        transformed_data = self._ppl.run(raw, rewrap=True)

        return next(transformed_data)

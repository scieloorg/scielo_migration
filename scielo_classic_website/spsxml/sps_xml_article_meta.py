import logging

import plumber
from lxml import etree as ET

from scielo_classic_website.htmlbody.html_body import HTMLContent
from scielo_classic_website.spsxml.sps_xml_attributes import (
    get_contrib_type,
    get_attribute_value,
)


def fix_html_text(html_text):
    """
    Remove tags b e troca tags i por italic
    """
    hc = HTMLContent(html_text)
    node = hc.tree.find(".")
    ET.strip_tags(node, "b")
    ET.strip_tags(node, "B")

    texts = []
    texts.append(node.text or '')
    last = None
    for item in node.findall(".//*"):
        if item.tag.lower() == "i":
            item.tag = "italic"
        texts.append(ET.tostring(item, encoding="utf-8").decode("utf-8"))
        last = item.tail
    texts.append(last or '')
    text = "".join(texts)
    if html_text != text:
        logging.debug(f"fix_html_text: antes: |{html_text}|")
        logging.debug(f"fix_html_text: depoi: |{text}|")
    return text


def create_node_with_fixed_html_text(element_name, html_text):
    """
    Remove tags b e troca tags i por italic
    """

    xml = f"<{element_name}>{html_text}</{element_name}>"
    hc = HTMLContent(xml)
    node = hc.tree.find(".")
    ET.strip_tags(node, "b")
    ET.strip_tags(node, "B")

    return node


def _create_date_element(element_name, attributes, date_text):
    # '<pub-date publication-format="electronic" date-type="pub">'
    if not date_text:
        return

    date_element = ET.Element(element_name)
    for attr_name, attr_value in attributes.items():
        date_element.set(attr_name, attr_value)
    year, month, day = date_text[:4], date_text[4:6], date_text[6:]
    labels = ("day", "month", "year")
    for label, value in zip(labels, (day, month, year)):
        if int(value) != 0:
            e = ET.Element(label)
            e.text = value
            date_element.append(e)
    return date_element


class XMLArticleMetaSciELOArticleIdPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        article_meta = xml.find("./front/article-meta")

        article_id_items = [
            {
                "value": raw.scielo_pid_v1,
                "pub-id-type": "publisher-id",
                "specific-use": "scielo-v1",
            },
            {
                "value": raw.scielo_pid_v2,
                "pub-id-type": "publisher-id",
                "specific-use": "scielo-v2",
            },
            {
                "value": raw.scielo_pid_v3,
                "pub-id-type": "publisher-id",
                "specific-use": "scielo-v3",
            },
            {"value": raw.aop_pid, "specific-use": "previous-pid"},
            {"value": raw.internal_sequence_id, "pub-id-type": "other"},
        ]

        for item in article_id_items:
            value = item.get("value")
            if value:
                article_id = ET.Element("article-id")
                for attr_name in ("pub-id-type", "specific-use"):
                    attr_value = item.get(attr_name)
                    if attr_value:
                        article_id.set(attr_name, attr_value)

                article_id.text = value
                article_meta.append(article_id)
        return data


class XMLArticleMetaArticleIdDOIPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.doi:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        article_id = ET.Element("article-id")
        article_id.set("pub-id-type", "doi")
        article_id.text = raw.doi

        xml.find("./front/article-meta").append(article_id)

        return data


class XMLArticleMetaArticleCategoriesPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data
        if not raw.original_section:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        subject_group = ET.Element("subj-group")
        subject_group.set("subj-group-type", "heading")

        subject = ET.Element("subject")
        subject.text = raw.get_section_title(raw.original_language)

        subject_group.append(subject)

        article_categories = ET.Element("article-categories")
        article_categories.append(subject_group)

        xml.find("./front/article-meta").append(article_categories)

        return data


class XMLArticleMetaTitleGroupPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        article_title = create_node_with_fixed_html_text(
            "article-title", raw.original_title)

        titlegroup = ET.Element("title-group")
        titlegroup.append(article_title)

        xml.find("./front/article-meta").append(titlegroup)

        return data


class XMLArticleMetaTranslatedTitleGroupPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data
        if not raw.translated_titles:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        for item in raw.translated_titles:
            trans_title = create_node_with_fixed_html_text(
                "trans-title", item["text"])

            trans_titlegrp = ET.Element("trans-title-group")
            trans_titlegrp.set(
                "{http://www.w3.org/XML/1998/namespace}lang", item["language"]
            )
            trans_titlegrp.append(trans_title)

            xml.find("./front/article-meta/title-group").append(trans_titlegrp)

        return data


class XMLArticleMetaContribGroupPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.authors:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        contrib_group = ET.Element("contrib-group")
        for author in raw.authors:
            contrib_name = ET.Element("name")

            # cria os elementos surname e given-names em name
            for tag, attr_name in zip(
                ("surname", "given-names"), ("surname", "given_names")
            ):
                value = author.get(attr_name)
                if value:
                    elem = ET.Element(tag)
                    elem.text = value
                    contrib_name.append(elem)

            # cria o elemento contrib e seu atributo contrib-type
            contrib = ET.Element("contrib")
            try:
                contrib_type = get_contrib_type(author["role"])
            except KeyError:
                contrib_type = "author"
            contrib.set("contrib-type", contrib_type)

            # contrib-id (lattes e orcid)
            for _contrib_id_type in ("lattes", "orcid"):
                try:
                    _contrib_id_value = author[_contrib_id_type]
                except KeyError:
                    continue
                else:
                    contrib_id = ET.Element("contrib-id")
                    contrib_id.set("contrib-id-type", _contrib_id_type)
                    contrib_id.text = _contrib_id_value
                    contrib.append(contrib_id)

            # inclui name como filho de contrib
            contrib.append(contrib_name)

            # crie os xref de contrib
            for xref_rid in author.get("xref", "").split(" "):
                if xref_rid:
                    xref = ET.Element("xref")
                    xref.set("ref-type", "aff")
                    xref.set("rid", xref_rid)
                    contrib.append(xref)

            contrib_group.append(contrib)

        xml.find("./front/article-meta").append(contrib_group)

        return data


class XMLArticleMetaAffiliationPipe(plumber.Pipe):
    def _addrline(self, affiliation):
        addrline = None
        for tag in ("city", "state"):
            try:
                value = affiliation[tag]
            except KeyError:
                pass
            else:
                elem = ET.Element("named-content")
                elem.set("content-type", tag)
                elem.text = value
                if addrline is None:
                    addrline = ET.Element("addr-line")
                addrline.append(elem)
        return addrline

    def transform(self, data):
        raw, xml = data

        attribs = ("orgname", "div", "div1", "div2", "div3")
        content_types = ("orgname", "orgdiv1", "orgdiv1", "orgdiv2", "orgdiv3")

        for affiliation in raw.affiliations:
            aff = ET.Element("aff")
            try:
                aff.set("id", affiliation["id"])
            except KeyError:
                pass

            for attr, content_type in zip(attribs, content_types):
                try:
                    value = affiliation[attr]
                except KeyError:
                    pass
                else:
                    elem = ET.Element("institution")
                    elem.set("content-type", content_type)
                    elem.text = value
                    aff.append(elem)

            addrline = self._addrline(affiliation)
            if addrline is not None:
                elem = ET.Element("addr-line")
                elem.extend(addrline)
                aff.append(elem)

            try:
                aff_country = affiliation["country"]
            except KeyError:
                pass
            else:
                std_country = get_attribute_value("country", aff_country)
                if std_country:
                    elem = ET.Element("country")
                    elem.text = aff_country
                    elem.set("country", std_country["code"])
                    aff.append(elem)

            try:
                value = affiliation["email"]
            except KeyError:
                pass
            else:
                elem = ET.Element("email")
                elem.text = value
                aff.append(elem)

            xml.find("./front/article-meta").append(aff)

        return data


class XMLArticleMetaPublicationDatesPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.document_publication_date and not raw.issue_publication_date and not raw.processing_date:
            raise plumber.UnmetPrecondition()

    def _node_pub_date(self, date_text, date_type):
        # '<pub-date publication-format="electronic" date-type="pub">'
        if not date_text:
            return

        attributes = dict(
            [
                ("publication-format", "electronic"),
                ("date-type", date_type),
            ]
        )
        pubdate = _create_date_element("pub-date", attributes, date_text)

        return pubdate

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        articlemeta = xml.find("./front/article-meta")

        pubdate = self._node_pub_date(raw.document_publication_date or raw.processing_date, "pub")
        if pubdate is not None:
            articlemeta.append(pubdate)

        pubdate = self._node_pub_date(raw.issue_publication_date, "collection")
        if pubdate is not None:
            articlemeta.append(pubdate)
        return data


class XMLArticleMetaIssueInfoPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        articlemeta = xml.find("./front/article-meta")

        if raw.volume:
            elem = ET.Element("volume")
            elem.text = raw.volume
            articlemeta.append(elem)

        if raw.issue_number and raw.issue_number != "ahead":
            elem = ET.Element("issue")
            elem.text = raw.issue_number
            articlemeta.append(elem)

        if raw.supplement:
            elem = ET.Element("supplement")
            elem.text = raw.supplement
            articlemeta.append(elem)

        return data


class XMLArticleMetaElocationInfoPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.elocation:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        elocation = ET.Element("elocation-id")
        elocation.text = raw.elocation

        articlemeta = xml.find("./front/article-meta")
        articlemeta.append(elocation)

        return data


class XMLArticleMetaPagesInfoPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.start_page:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        fpage = ET.Element("fpage")
        fpage.text = raw.start_page

        seq = raw.start_page_sequence
        if seq:
            fpage.set("seq", seq)

        articlemeta = xml.find("./front/article-meta")
        articlemeta.append(fpage)

        if raw.end_page:
            lpage = ET.Element("lpage")
            lpage.text = raw.end_page
            articlemeta.append(lpage)

        return data


class XMLArticleMetaHistoryPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        history = ET.Element("history")

        dates = {
            "received": raw.receive_date_iso,
            "rev-recd": raw.review_date_iso,
            "accepted": raw.acceptance_date_iso,
        }

        for date_type, date_ in dates.items():
            if date_:
                attributes = {"date-type": date_type}
                elem = _create_date_element("date", attributes, date_)
                history.append(elem)

        if len(history.findall("date")) > 0:
            xml.find("./front/article-meta").append(history)

        return data


class XMLArticleMetaAbstractsPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        articlemeta = xml.find("./front/article-meta")

        if raw.original_abstract:
            p = create_node_with_fixed_html_text("p", raw.original_abstract)

            abstract = ET.Element("abstract")
            abstract.append(p)

            articlemeta.append(abstract)

        if raw.translated_abstracts:
            langs = list((raw.translated_htmls or {}).keys())

            for item in raw.translated_abstracts:
                if item["language"] in langs:
                    continue

                p = create_node_with_fixed_html_text("p", item["text"])

                abstract = ET.Element("trans-abstract")
                abstract.set(
                    "{http://www.w3.org/XML/1998/namespace}lang", item["language"]
                )
                abstract.append(p)

                articlemeta.append(abstract)

        return data


class XMLArticleMetaKeywordsPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.keywords:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        translated_langs = list((raw.translated_htmls or {}).keys())

        articlemeta = xml.find("./front/article-meta")

        for lang, keywords in raw.keywords_groups.items():
            if lang in translated_langs:
                continue

            kwdgroup = ET.Element("kwd-group")
            kwdgroup.set("{http://www.w3.org/XML/1998/namespace}lang", lang)
            kwdgroup.set("kwd-group-type", "author-generated")

            for item in keywords:
                kwd = create_node_with_fixed_html_text("kwd", item)
                kwdgroup.append(kwd)
            articlemeta.append(kwdgroup)

        return data


class XMLArticleMetaPermissionPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data

        if not raw.permissions:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        articlemeta = xml.find("./front/article-meta")

        permissions = ET.Element("permissions")
        dlicense = ET.Element("license")
        dlicense.set("license-type", "open-access")
        dlicense.set("{http://www.w3.org/1999/xlink}href", raw.permissions["url"])
        dlicense.set("{http://www.w3.org/XML/1998/namespace}lang", "en")

        licensep = ET.Element("license-p")
        licensep.text = raw.permissions["text"]

        dlicense.append(licensep)
        permissions.append(dlicense)
        articlemeta.append(permissions)

        return data


class XMLArticleMetaSelfUriPipe(plumber.Pipe):
    """Adiciona tag `self-uri` ao article-meta do artigo.
    As tags `self-uri` disponibilizam fontes alternativas para o
    texto completo."""

    def precond(data):
        raw, _ = data

        if not raw.data.get("fulltexts"):
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data
        articlemeta = xml.find("./front/article-meta")

        # data injection in Document
        for item in raw.data.get("fulltexts", []):
            self_uri = ET.Element("self-uri")
            self_uri.set("{http://www.w3.org/1999/xlink}href", item["uri"])
            self_uri.set("{http://www.w3.org/XML/1998/namespace}lang", item["lang"])
            self_uri.text = item.get("uri_text") or ""
            articlemeta.append(self_uri)

        return data


class XMLArticleMetaCountsPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        articlemeta = xml.find("./front/article-meta")

        counts = articlemeta.find("counts")
        if counts is None:
            counts = ET.Element("counts")

        body_node = xml.find("./body")
        if body_node is not None:
            elems = [
                (
                    "fig-count",
                    len(body_node.findall(".//fig[@id]"))
                    + len(body_node.findall(".//fig-group[@id]")),
                ),
                (
                    "table-count",
                    len(body_node.findall(".//table-wrap[@id]"))
                    + len(body_node.findall(".//table-wrap-group[@id]")),
                ),
                ("equation-count", len(body_node.findall(".//disp-formula[@id]"))),
            ]

            for elem_name, count in elems:
                count_elem = counts.find(elem_name)
                if count_elem is None:
                    count_elem = ET.Element(elem_name)
                count_elem.set("count", str(count))
                counts.append(count_elem)

        count_refs = ET.Element("ref-count")
        if raw.citations:
            count_refs.set("count", str(len(raw.citations)))
        else:
            count_refs.set("count", "0")
        counts.append(count_refs)

        try:
            startpage = int(raw.start_page or 0)
            endpage = int(raw.end_page or raw.start_page or 0)
            if 0 < startpage <= endpage:
                count_pages = ET.Element("page-count")
                count_pages.set("count", str(endpage - startpage + 1))
                counts.append(count_pages)
        except (ValueError, TypeError):
            pass

        articlemeta.append(counts)

        for subart in xml.findall("./sub-article"):
            frontstub = subart.find("front-stub")
            if frontstub is None:
                subart.append(ET.Element("front-stub"))

            counts = subart.find("front-stub/counts")
            if counts is None:
                counts = ET.Element("counts")

            body_node = xml.find("./body")
            if body_node is not None:

                elems = [
                    (
                        "fig-count",
                        len(body_node.findall(".//fig[@id]"))
                        + len(body_node.findall(".//fig-group[@id]")),
                    ),
                    (
                        "table-count",
                        len(body_node.findall(".//table-wrap[@id]"))
                        + len(body_node.findall(".//table-wrap-group[@id]")),
                    ),
                    ("equation-count", len(body_node.findall(".//disp-formula[@id]"))),
                ]

                for elem_name, count in elems:
                    count_elem = counts.find(elem_name)
                    if count_elem is None:
                        count_elem = ET.Element(elem_name)
                    count_elem.set("count", str(count))
                    counts.append(count_elem)

            frontstub.append(counts)
        return data


class XMLNormalizeSpacePipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        for node in xml.xpath(".//*"):
            if node.text and '  ' in node.text:
                node.text = " ".join(
                    [word for word in node.text.split() if word.strip()])
            if node.tail and '  ' in node.tail:
                node.tail = " ".join(
                    [word for word in node.tail.split() if word.strip()])
        return data

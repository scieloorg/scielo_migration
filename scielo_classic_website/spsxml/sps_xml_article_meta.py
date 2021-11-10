import plumber
from lxml import etree as ET


class XMLArticleMetaSciELOArticleIdPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        article_meta = xml.find('./front/article-meta')

        article_id_items = [
            {"value": raw.scielo_pid_v1, "pub-id-type": "publisher-id",
             "specific-use": "scielo-v1"},
            {"value": raw.scielo_pid_v2, "pub-id-type": "publisher-id",
             "specific-use": "scielo-v2"},
            {"value": raw.scielo_pid_v3, "pub-id-type": "publisher-id",
             "specific-use": "scielo-v3"},
            {"value": raw.aop_pid, "specific-use": "previous-pid"},
            {"value": raw.internal_sequence_id, "pub-id-type": "other"},
        ]

        for item in article_id_items:
            value = item.get("value")
            if value:
                article_id = ET.Element('article-id')
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

        article_id = ET.Element('article-id')
        article_id.set('pub-id-type', 'doi')
        article_id.text = raw.doi

        xml.find('./front/article-meta').append(article_id)

        return data


class XMLArticleMetaArticleCategoriesPipe(plumber.Pipe):
    def precond(data):
        raw, xml = data
        if not raw.original_section:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        subject_group = ET.Element('subj-group')
        subject_group.set('subj-group-type', 'heading')

        subject = ET.Element('subject')
        subject.text = raw.original_section

        subject_group.append(subject)

        article_categories = ET.Element('article-categories')
        article_categories.append(subject_group)

        xml.find('./front/article-meta').append(article_categories)

        return data


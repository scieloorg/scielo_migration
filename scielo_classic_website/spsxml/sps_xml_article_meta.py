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
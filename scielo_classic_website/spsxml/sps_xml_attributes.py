import os
import csv

from scielo_classic_website.config import (
    ATTRIBUTES_PATH,
)

from scielo_classic_website.attr_values import AttrValues


def _read_csv_file(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


def _get_dict(items):
    return {
        item["from"]: item["to"]
        for item in items
    }


def _load_values(filename):
    file_path = os.path.join(ATTRIBUTES_PATH, filename)
    return _get_dict(_read_csv_file(file_path))


def _get_file_path(filename):
    return os.path.join(ATTRIBUTES_PATH, filename)


class Country:
    # alpha_2_code,alpha_3_code,short_name_en,short_name_pt,short_name_es

    def __init__(self, items):
        self._indexed_by_code = {}
        self._indexed_by_name = {}
        for item in items:
            self._indexed_by_code[item['alpha_2_code']] = item
            self._indexed_by_code[item['alpha_3_code']] = item
            self._indexed_by_name[item['short_name_en']] = item
            self._indexed_by_name[item['short_name_pt']] = item
            self._indexed_by_name[item['short_name_es']] = item

    def name(self, code, lang=None):
        try:
            country = self._indexed_by_code[code]
        except KeyError:
            return
        if lang:
            return country.get(f"short_name_{lang}")

        for k in ("short_name_en", "short_name_pt", "short_name_es"):
            name = country.get(k)
            if name:
                return name

    def get(self, key):
        country = (
            self._indexed_by_code.get(key) or self._indexed_by_name.get(key)
        )
        if country:
            for k in ("short_name_en", "short_name_pt", "short_name_es"):
                name = country[k]
                if name:
                    country['name'] = name
                    break
            country['code'] = country['alpha_2_code']
            return country


ARTICLE_TYPES = _load_values('isis2sps_article_types.csv')

CONTRIB_ROLES = AttrValues(_read_csv_file(_get_file_path('contrib_roles.csv')))

file_path = _get_file_path("country.csv")
COUNTRY_ITEMS = Country(_read_csv_file(file_path))


def get_attribute_value(attribute_name, code, lang=None):
    if attribute_name == "country":
        return COUNTRY_ITEMS.get(code)
    if attribute_name == "country_name":
        return COUNTRY_ITEMS.name(code, lang)
    if attribute_name == "role":
        return CONTRIB_ROLES.get_sps_value(code)
    if attribute_name == "article-type":
        return ARTICLE_TYPES.get(code)
    return code

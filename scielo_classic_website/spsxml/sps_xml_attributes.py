import os
import csv

from scielo_classic_website.config import (
    ATTRIBUTES_PATH,
)

from scielo_migration.attr_values import AttrValues


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


def _load_countries(filename):
    file_path = os.path.join(ATTRIBUTES_PATH, filename)
    data = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data[row['alpha_2_code']] = row
    return data


class Country:

    def __init__(self, items):
        self._items = items

    def name(self, code):
        try:
            country = self._items[code]
        except KeyError:
            return

        for k in ("short_name_en", "short_name_pt", "short_name_es"):
            name = country.get(k)
            if name:
                return name


ARTICLE_TYPES = _load_values('isis2sps_article_types.csv')
COUNTRY_ITEMS = Country(_load_countries("country.csv"))

CONTRIB_ROLES = AttrValues(_read_csv_file(_get_file_path('contrib_roles.csv')))

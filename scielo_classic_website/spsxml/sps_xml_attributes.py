import csv
import os

from scielo_classic_website.attr_values import AttrValues
from scielo_classic_website.config import ATTRIBUTES_PATH
from scielo_classic_website.settings.attributes.country import COUNTRY

ISIS2SPS_ARTICLE_TYPES_CSV = "isis2sps_article_types.csv"
CONTRIB_ROLES_CSV = "contrib_roles.csv"
COUNTRY_CSV = "country.csv"


def _read_csv_file(file_path):
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


def _get_dict(items):
    return {item["from"]: item["to"] for item in items}


def _load_values(filename):
    file_path = _get_file_path(filename)
    return _get_dict(_read_csv_file(file_path))


def _get_file_path(filename):
    file_path = os.path.join(os.path.abspath('..'), "settings", "attributes")
    if os.path.isfile(file_path):
        return file_path

    file_path = os.path.join(ATTRIBUTES_PATH, filename)
    if os.path.isfile(file_path):
        return file_path


def country_name(code, lang=None):
    try:
        country = COUNTRY[code]
    except KeyError:
        return
    if lang:
        return country.get(f"short_name_{lang}")

    for k in ("short_name_en", "short_name_pt", "short_name_es"):
        name = country.get(k)
        if name:
            return name


def country_get(code):
    try:
        country = COUNTRY[code]
    except KeyError:
        return

    for k in ("short_name_en", "short_name_pt", "short_name_es"):
        name = country[k]
        if name:
            country["name"] = name
            break
    country["code"] = country["alpha_2_code"]
    return country


ARTICLE_TYPES = _load_values(ISIS2SPS_ARTICLE_TYPES_CSV)

CONTRIB_ROLES = AttrValues(_read_csv_file(_get_file_path(CONTRIB_ROLES_CSV)))

file_path = _get_file_path(COUNTRY_CSV)


def get_attribute_value(attribute_name, code, lang=None):
    if attribute_name == "country":
        return country_get(code)
    if attribute_name == "country_name":
        return country_name(code, lang)
    if attribute_name == "role":
        return CONTRIB_ROLES.get_sps_value(code)
    if attribute_name == "article-type":
        return ARTICLE_TYPES.get(code)
    return code

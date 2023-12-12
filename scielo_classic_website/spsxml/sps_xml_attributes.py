import csv
import os

from scielo_classic_website.attributes.country import COUNTRY
from scielo_classic_website.attributes.contrib_type import CONTRIB_TYPE
from scielo_classic_website.attributes.article_type import ARTICLE_TYPE


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
    return code


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


def get_contrib_type(code):
    try:
        return CONTRIB_TYPE[code]
    except KeyError:
        return "author"


def get_article_type(code):
    try:
        return ARTICLE_TYPE[code]
    except KeyError:
        return code


def get_attribute_value(attribute_name, code, lang=None):
    if attribute_name == "country":
        return country_get(code)
    if attribute_name == "country_name":
        return country_name(code, lang)
    if attribute_name == "role":
        return get_contrib_type(code)
    if attribute_name == "article-type":
        return get_article_type(code)
    return code

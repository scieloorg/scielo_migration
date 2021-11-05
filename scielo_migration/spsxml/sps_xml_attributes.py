import os
import csv

from scielo_migration.config import (
    ATTRIBUTES_PATH,
)


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


ARTICLE_TYPES = _load_values('isis2sps_article_types.csv')

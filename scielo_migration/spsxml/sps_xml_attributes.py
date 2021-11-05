import os
from scielo_migration.attr_values import (
    AttrValues,
    read_csv_file,
)


PATH = 'scielo_migration/attr_values_data'


def _get_items(filename):
    path = os.path.join(PATH, filename)
    return read_csv_file(path)


ARTICLE_TYPES = AttrValues(_get_items('article_types.csv'))
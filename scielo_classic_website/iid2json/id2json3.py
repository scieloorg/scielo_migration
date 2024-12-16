"""
Module converts file.id content from:

```
!ID 000001
!v002!1414-431X-bjmbr-1414-431X20165409.xml
!v012!New record of Blepharicnema splendens^len
!v049!^cAA970^lpt^tBiodiversidade e Conservação
!v049!^cAA970^len^tBiodiversity and Conservation
```

to JSON

```
[
   "v002": [
       {"_": "1414-431X-bjmbr-1414-431X20165409.xml"}
   ],
   "v012": [
       {"_": "New record of Blepharicnema splendens", "l": "en"}
   ],
   "v049": [
       {"c": "AA970", "l": "pt", "t": "Biodiversidade e Conservação"},
       {"c": "AA970", "l": "en", "t": "Biodiversity and Conservation"},
   ]
]
```

"""
import logging


class IssueIdError(Exception):
    ...


class ArticleIdError(Exception):
    ...


def get_id_function(db_type):
    id_function = article_id
    if db_type == "title":
        id_function = journal_id
    elif db_type == "issue":
        id_function = issue_id
    return id_function


def pids_and_their_records(id_file_path, db_type):
    logging.info("pids_and_their_records %s %s" % (id_file_path, db_type))
    if not id_file_path:
        return []
    id_function = get_id_function(db_type)

    rows = _get_id_file_rows(id_file_path)

    records = _join_id_file_rows_and_return_records(rows)

    return _get_id_and_json_records(records, id_function)


def get_doc_records(id_file_path):
    for item_id, records in pids_and_their_records(id_file_path, "artigo"):
        record_type = None
        if records:
            record_type = _get_value(records[0], "v706")

        if record_type == "i":
            yield {"issue_id": item_id, "issue_data": records[0]}
        elif record_type == "o":
            if len(item_id) == 23:
                i_id = item_id[1:18]
                yield {"doc_id": item_id, "doc_data": records, "i_id": i_id}
            else:
                yield {"invalid_records": True, "item_id": item_id, "records": records}
        else:
            yield {"invalid_records": True, "item_id": item_id, "records": records}


def _get_value(data, tag):
    """
    Returns first value of field `tag`
    """
    # data['v880'][0]['_']

    if len(tag) < 4:
        tag = "v" + tag[1:].zfill(3)
    try:
        return data[tag][0]["_"]
    except (KeyError, IndexError):
        return None


def _get_items(data, tag):
    """
    Returns first value of field `tag`
    """
    # data['v880'][0]['_']
    try:
        return [item["_"] for item in data[tag]]
    except KeyError:
        return None


def _parse_field_content(content):
    if not content:
        return
    if "^" not in content:
        return {"_": content}
    if not content.startswith("^"):
        content = "^_" + content
    content = content.replace("\\^", "ESCAPECIRC")
    subfields = content.split("^")
    items = []
    for subf in subfields:
        if not subf:
            continue
        s = subf[0]
        if s in "_abcdefghijklmnopqrstuvwxyz123456789":
            items.append([s, subf[1:]])
        else:
            items.append(["", "\\^" + s + subf[1:]])

    for i, item in enumerate(items):
        s, v = item
        if s == "":
            items[i - 1][1] += v
            items[i][1] = ""

    d = {}
    for s, v in items:
        if s and v:
            d[s] = v
    return d


def _parse_field(data):
    second_excl_char_pos = data[1:].find("!") + 1
    tag = data[1:second_excl_char_pos]
    subfields = _parse_field_content(data[second_excl_char_pos + 1 :])
    return (tag, subfields)


def _build_record(record):
    if not record:
        return
    data = {}
    for k, v in record:
        if not k or not v:
            continue
        data.setdefault(k, [])
        data[k].append(v)
    return data


def journal_id(data):
    return _get_value(data, "v400")


def issue_id(data):
    try:
        return "".join(
            [
                _get_value(data, "v035"),
                _get_value(data, "v036")[:4],
                _get_value(data, "v036")[4:].zfill(4),
            ]
        )
    except Exception as e:
        raise IssueIdError(f"Unable to return issue_id for {data}: {e} {type(e)}")


def article_id(data):
    record_type = _get_value(data, "v706")
    if not record_type:
        return
    if record_type == "i":
        return issue_id(data)
    try:
        try:
            return _get_value(data, "v880")[:23]
        except (TypeError, IndexError, KeyError):
            # bases em serial não tem o campo v880 inserido no GeraPadrao
            # pode-se agrupar os registros pelo v702 (path do XML ou HTML)
            return _get_value(data, "v702")
    except Exception as e:
        raise ArticleIdError(f"Unable to return article_id for {data}: {e} {type(e)}")


def _get_fields_and_their_content(content):
    if not content:
        return
    rows = content.splitlines()
    return [_parse_field(row) for row in rows if row]


# ok
def _get_id_file_rows(id_file_path):
    """
    Obtém uma lista de linhas do arquivo `id_file_path`

    Parameters
    ----------
    id_file_path: str
        arquivo ID de uma base de dados ISIS

    Returns
    -------
    list of strings
    """
    try:
        with open(id_file_path, "r", encoding="iso-8859-1") as fp:
            for item in fp.readlines():
                yield item.strip()
    except FileNotFoundError:
        return []


# ok
def _join_id_file_rows_and_return_records(id_file_rows):
    """
    Junta linhas `id_file_rows` que formam registros (str) e os retorna

    Parameters
    ----------
    id_file_rows: list of str
        linhas do arquivo ID

    Returns
    -------
    list of strings
    """
    record_rows = []
    for row in id_file_rows or []:
        if row.startswith("!ID "):
            if len(record_rows):
                # junta linhas que formam uma string
                # que corresponde a um registro e o retorna
                yield "\n".join(record_rows)

                # inicia um novo grupo de linhas de registro
                record_rows = []
        elif not row.startswith("!v"):
            # trata quebra de linha dentro de campo
            if record_rows:
                record_rows[-1] += " " + row.strip()
        else:
            # adiciona linhas ao registro
            record_rows.append(row.strip())
    # junta linhas que formam uma string
    # que corresponde a um registro e o retorna
    yield "\n".join(record_rows)


# ok
def _get_id_and_json_records(records, get_id_function):
    """
    Given `records` e `get_id_function`, returns `_id` and `json_records`

    Parameters
    ----------
    records: list of str
        linhas do arquivo ID
    get_id_function: callable
        função que gera o ID do registro

    Returns
    -------
    list of strings
    """
    item_id = None
    item_records = []
    for record_content in records:
        if not record_content:
            continue
        fields = _get_fields_and_their_content(record_content)
        data = _build_record(fields)
        if not data:
            continue

        new_id = get_id_function(data)

        if item_id and new_id != item_id:
            # item_id changed

            # returns current _id, item_records
            yield (item_id, item_records)

            # init a new group of records
            item_records = []

        item_id = new_id
        # add `data` to `item_records`
        item_records.append(data)
    # returns item_id, item_records
    yield (item_id, item_records)

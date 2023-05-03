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
    logging.info("pids_and_their_records rows=%s" % rows)

    records = _join_id_file_rows_and_return_records(rows)
    logging.info("pids_and_their_records records=%s" % records)
    return _get_id_and_json_records(records, id_function)


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
    except:
        print("issue_id")
        print(data)
        raise


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
        logging.exception(e)
        raise


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
    _id = None
    _id_records = []
    for record_content in records:
        if not record_content:
            continue
        fields = _get_fields_and_their_content(record_content)
        data = _build_record(fields)
        if not data:
            continue
        _next_id = get_id_function(data)
        if _id and _next_id != _id:
            # _id changed

            # returns current _id, _id_records
            yield (_id, _id_records)

            # init a new group of records
            _id_records = []

        # update `_id` with `_next_id`
        _id = _next_id
        # add `data` to `_id_records`
        _id_records.append(data)
    # returns current _id, _id_records
    yield (_id, _id_records)

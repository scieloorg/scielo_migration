from copy import deepcopy


def build_object(obj, record_as_dict):
    """
    Cria atributos no obj baseado em `data_dict`
    """
    for name, data in record_as_dict.items():
        setattr(obj, name, data)


def _get_tag_content(record, tag):
    # v10 or v010
    try:
        return record[tag]
    except KeyError:
        number = str(int(tag[1:]))
        return record.get("v" + number) or record.get("v" + number.zfill(3))


class RawRecord:
    def __init__(self, record):
        self._record = record
        self._fix_function = lambda x: x

    @property
    def fix_function(self):
        return self._fix_function

    @fix_function.setter
    def fix_function(self, func):
        self._fix_function = func

    @property
    def rec_type(self):
        try:
            return self._record["v706"][0]["_"]
        except:
            return

    def get_items(self, tag, subfields):
        if not self._record.get(tag):
            return []
        for item in self._record[tag]:
            if isinstance(item, dict):
                _item = {}
                for k, v in item.items():
                    try:
                        _k = subfields[k]
                    except KeyError:
                        _k = k
                    _item[_k] = self.fix_function(v)
                yield _item
            else:
                yield self.fix_function(_item)

    def get_field_content(self, tag, subfields, single):
        items = []
        for item in self.get_items(tag, subfields):
            ignore_subfields = (
                len(subfields) == 1 and subfields.get("_") is not None
            ) or len(subfields) == 0
            if isinstance(item, dict) and ignore_subfields:
                data = list(item.values())
                items.append(data[0])
            else:
                items.append(item)
        if single:
            try:
                return items[0]
            except IndexError:
                return None
        return items

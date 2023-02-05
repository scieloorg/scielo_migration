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

    @property
    def fix_function(self):
        return self._fix_function or (lambda x: x)

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
        for item in self._record[tag]:
            if isinstance(item, dict):
                _item = {}
                for k, v in item.items():
                    try:
                        _item[subfields[k]] = self.fix_function(v)
                    except KeyError:
                        _item[k] = self.fix_function(item[k])
                yield _item
            else:
                yield self.fix_function(item)

    def get_field_content(self, tag, field_name, subfields, single):
        for item in self.get_items(tag, subfields):
            if isinstance(item, dict) and len(subfields) == 1 and subfields.get("_"):
                data = list(item.values())
                if data:
                    if single:
                        return data[0]
                    else:
                        yield data[0]
            else:
                if single:
                    return item
                else:
                    yield item

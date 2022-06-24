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


class MetaRecord:

    def __init__(self, record,
                 multi_val_tags=None,
                 data_dictionary=None,
                 ):
        self._record = record
        self._multi_val_tags = multi_val_tags or []
        self._data_dictionary = data_dictionary or {}

    @property
    def rec_type(self):
        try:
            return self._record["v706"][0]["_"]
        except:
            return

    def get_single_value(self, tag):
        """
        Retorna o conteúdo do campo `tag` que não se repete e não tem subcampo
        """
        try:
            return self._record[tag][0]["_"]
        except (KeyError, IndexError):
            return

    def get_multi_value(self, tag):
        """
        Retorna o conteúdo do campo `tag` que se repete e não tem subcampo
        """
        try:
            return [item["_"] for item in self._record[tag]]
        except KeyError:
            return

    def get_field_content(self, tag, subfields=None,
                          single=False, simple=False):
        """
        Retorna o conteúdo do campo `tag`. Usa `subfields` para traduzir
        os subcampos do ISIS em nomes mais expressivos

        Parameters
        ----------
        tag: str
            no formato "v010"
        subfields: dict
            keys: caracter representa subcampos no ISIS
            values: tradução dos subcampos
                Exemplo de valor de `subfields`:
                ```
                {
                    "s": "surname",
                    "n": "given-names",
                    "r": "role",
                }
                ```
        single: bool
            `True` returns one occurrence, False returns `list`
        simple: bool
            `True` returns `value` instead of `{"_": value}`

        Returns
        -------
        list of dict
        ```
        [
            {"surname": "", "given-names": "", "role": ""},
            {"surname": "", "given-names": "", "role": ""},
            {"surname": "", "given-names": "", "role": ""},
        ]
        ```
        """
        if tag in self._multi_val_tags:
            single = False
        if subfields and len(subfields):
            simple = False

        # v10 or v010
        tag_content = _get_tag_content(self._record, tag)
        if not tag_content:
            if single and simple:
                return None
            if single:
                return {}
            return []

        if simple and single:
            # str and ocorrencia única
            try:
                return tag_content[0]["_"]
            except (IndexError, KeyError, TypeError):
                return None

        if single:
            # dict and ocorrencia única
            try:
                return self._get_occ(tag_content[0], subfields or {})
            except (IndexError, KeyError, TypeError) as e:
                print(e)
                return {}

        if simple:
            # str and ocorrencia multipla
            try:
                return [item["_"] for item in tag_content]
            except (IndexError, KeyError, TypeError):
                return []

        # dict and multiple
        return [
            self._get_occ(occ, subfields or {})
            for occ in tag_content
        ]

    def _get_occ(self, occ, subfields):
        """
        Para esta ocorrência do campo, retorna os subcampos renomeados pela
        correspondência dada por `subfields`.
        Caso um subcampo não tenha correspondência, ele será retornado com o
        nome original do subcampo.

        Exemplo:
        Para ocorrência do campo: `{"s": "Smith", "n": "Nora", "r": "author"}`
        Com `subfields`: `{"s": "surname", "r": "role"}`
        Resultado: `{"surname": "Smith", "n": "Nora", "role": "author"}`

        Parameters
        ----------
        occ: dict
            conteúdo de uma ocorrência do campo
        subfields: dict
            keys: caracter representa subcampos no ISIS
            values: tradução dos subcampos
                Exemplo:
                ```
                {
                    "s": "surname",
                    "n": "given-names",
                    "r": "role",
                }
                ```
        Returns
        -------
        dict
            ```
            {"surname": "", "given-names": "", "role": "", "x": "", "y": ""}
            ```
        """
        return {
            subfields.get(subf_char) or subf_char: subf_value
            for subf_char, subf_value in occ.items()
        }

    def get_named_field(self, tag, field_name=None, subfields=None,
                        single=False, simple=False):
        """
        Retorna o conteúdo do campo `tag` em formato `dict`

        Parameters
        ----------
        tag: str
            no formato "v010"
        field_name: str
            nome para usar no lugar de "v010"
        subfields: dict
            keys: caracter representa subcampos no ISIS
            values: tradução dos subcampos
                Exemplo de valor de `subfields`:
                ```
                {
                    "s": "surname",
                    "n": "given-names",
                    "r": "role",
                }
                ```
        single: bool
            `True` returns one occurrence, False returns `list`
        simple: bool
            `True` returns `value` instead of `{"_": value}`

        Returns
        -------
        dict
            ```
            {"authors":
                {"surname": "", "given-names": "", "role": ""},
                {"surname": "", "given-names": "", "role": ""},
                {"surname": "", "given-names": "", "role": ""},
            }
            ```
        """
        return {
            field_name or tag:
            self.get_field_content(
                tag, subfields, single, simple)
        }

    def get_record_subset_as_dict(self, data_dict):
        """
        Retorna somente os campos do registro, indicados no `data_dict`,
        em formato de dicionário

        Parameters
        ----------
        data_dict:
            dicionário de dados para "traduzir" o registro

        Returns
        -------
        dict
            ```
            {"tag": {"field_name": "authors", "subfields": {},
                     "single": True, "simple": True}}
            ```
        """
        if not data_dict:
            raise ValueError(
                """ERROR: MetaRecord.get_record_subset_as_dict requires  """
                """`data_dict` as dictionary such as """
                """{"tag": {"field_name": "authors", "subfields": {},"""
                """ "single": True, "simple": True} }"""
            )

        record = {}
        for tag, template in data_dict.items():
            field_name = template.get("field_name") or tag
            subfields = template.get("subfields") or {}
            single = not template.get("is_multi_val")
            simple = not subfields
            record.update(
                self.get_named_field(
                    tag, field_name, subfields, single, simple,
                )
            )
        return record

    def get_full_record_as_dict(self, data_dict=None):
        """
        Retorna todos os campos do registro, inclusive aqueles
        que não estão presentes em `data_dict`. Na ausência de `data_dict`,
        usa `self._data_dictionary`.

        Parameters
        ----------
        data_dict: dict
            dicionário de dados para "traduzir" o registro

        Returns
        -------
        dict
            ```
            {"tag": {"field_name": "authors", "subfields": {},
                     "single": True, "simple": True}}
            ```
        """
        data_dict = data_dict or self._data_dictionary
        if not data_dict:
            return deepcopy(self._record)

        record = {}
        for tag in self._record.keys():
            try:
                template = data_dict[tag]
            except KeyError:
                # print(tag, data_dict.keys())
                field_name = tag
                subfields = {}
                single = False
                simple = False
            else:
                field_name = template.get("field_name") or tag
                subfields = template.get("subfields") or {}
                single = not template.get("is_multi_val")
                simple = not subfields
            record.update(
                self.get_named_field(
                    tag, field_name, subfields, single, simple,
                )
            )
        return record

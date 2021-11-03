from copy import deepcopy


def build_object(obj, record_as_dict):
    """
    Cria atributos no obj baseado em `data_dict`
    """
    for name, data in record_as_dict.items():
        setattr(obj, name, data)


class MetaRecord:

    def __init__(self, record,
                 no_repetition_tags=None, no_subfield_tags=None,
                 data_dictionary=None,
                 ):
        self._record = record
        self._no_repetition_tags = no_repetition_tags or []
        self._no_subfield_tags = no_subfield_tags or []
        self._data_dictionary = data_dictionary or {}

    @property
    def rec_type(self):
        try:
            return self._record["v706"][0]["_"]
        except:
            return

    def get_simple_content(self, tag):
        """
        Retorna o conteúdo do campo `tag` que não se repete e não tem subcampo
        """
        try:
            return self._record[tag][0]["_"]
        except (KeyError, IndexError):
            return

    def get_multi_content(self, tag):
        """
        Retorna o conteúdo do campo `tag` que se repete e não tem subcampo
        """
        try:
            return [item["_"] for item in self._record[tag]]
        except KeyError:
            return

    def get_field_content(self, tag, subfields=None,
                          no_repetition=False, no_subfield=False):
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
        no_repetition: bool
            `True` returns one occurrence, False returns `list`
        no_subfield: bool
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
        no_repetition = no_repetition or tag in self._no_repetition_tags
        no_subfield = no_subfield or tag in self._no_subfield_tags

        try:
            if no_subfield and no_repetition:
                return self._record[tag][0]["_"]
            elif no_repetition:
                return self._record[tag][0]
            elif no_subfield:
                return [item["_"] for item in self._record[tag]]
        except (IndexError, KeyError):
            pass

        return [
            self._get_occ(occ, subfields or {})
            for occ in self._record.get(tag) or []
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
                        no_repetition=False, no_subfield=False):
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
        no_repetition: bool
            `True` returns one occurrence, False returns `list`
        no_subfield: bool
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
                tag, subfields, no_repetition, no_subfield)
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
                     "no_repetition": True, "no_subfield": True}}
            ```
        """
        if not data_dict:
            raise ValueError(
                """ERROR: MetaRecord.get_record_subset_as_dict requires  """
                """`data_dict` as dictionary such as """
                """{"tag": {"field_name": "authors", "subfields": {},"""
                """ "no_repetition": True, "no_subfield": True} }"""
            )

        record = {}
        for tag, template in data_dict.items():
            field_name = template.get("field_name") or tag
            subfields = template.get("subfields") or {}
            no_repetition = template.get("no_repetition") or False
            no_subfield = template.get("no_subfield") or False
            record.update(
                self.get_named_field(
                    tag, field_name, subfields, no_repetition, no_subfield,
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
                     "no_repetition": True, "no_subfield": True}}
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
                no_repetition = False
                no_subfield = False
            else:
                field_name = template.get("field_name") or tag
                subfields = template.get("subfields") or {}
                no_repetition = template.get("no_repetition") or False
                no_subfield = template.get("no_subfield") or False
            record.update(
                self.get_named_field(
                    tag, field_name, subfields, no_repetition, no_subfield,
                )
            )
        return record

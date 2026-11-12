"""
Interface flexível para arquivos ``.id`` (saída do utilitário ``i2id``) das
bases ISIS do site clássico: ``title`` (journal), ``issue`` e ``artigo``.

Complementa ``ClassicWebsite``: em vez de depender da estrutura de
diretórios do site clássico, basta informar o tipo da base e o caminho
do arquivo ``.id``.

Características
---------------
- Leitura em *streaming*: o arquivo é lido linha a linha e somente um item
  (grupo de registros com o mesmo PID) é mantido em memória por vez.
- Parse preguiçoso: para identificar o PID e a data, apenas os poucos campos
  necessários são decodificados. O JSON completo (``item.records``) só é
  montado quando acessado, ou seja, itens descartados por filtro (data, PID)
  não têm custo de conversão.
- Filtros por data (``since`` / ``until``) e por PID.
- Índice opcional ``pid -> offset`` para acesso direto (``seek``) a itens.
- Artigo: inclui os registros "p" que ficam fora do arquivo principal
  (``{base}/artigo/p/<pid>``), se ``p_records_base_paths`` for informado.
- ``pids_and_records()`` mantém compatibilidade com
  ``id2json3.pids_and_their_records``.

Exemplo
-------
>>> id_file = ClassicIdFile("issue", "/bases/issue/issue.id")
>>> for item in id_file.items(since="2024-01-01"):
...     print(item.pid, item.date)
...     data = item.records  # parse completo apenas aqui
>>> id_file = ClassicIdFile("artigo", "/bases-work/abc/abc.id")
>>> for item in id_file.items(kind="document", until="2023"):
...     print(item.pid, item.date, len(item.records))
"""

import datetime
import os

from scielo_classic_website.iid2json import id2json3

TITLE = "title"
ISSUE = "issue"
ARTIGO = "artigo"

DB_TYPE_ALIASES = {
    "title": TITLE,
    "journal": TITLE,
    "issue": ISSUE,
    "artigo": ARTIGO,
    "article": ARTIGO,
    "document": ARTIGO,
}

# campos que identificam o item (PID) por tipo de base
ID_TAGS = {
    TITLE: ("v400",),
    ISSUE: ("v035", "v036"),
    ARTIGO: ("v706", "v880", "v702", "v035", "v036"),
}

# ordem dos tipos de registro (v706) de um documento na base artigo.
# Tipos podem faltar, mas a ordem não se inverte (ex.: "o" nunca vem depois
# de "h"); "p", "c" e "r" se repetem em sequência.
ARTIGO_RECORD_TYPES_ORDER = {
    rec_type: rank for rank, rec_type in enumerate("ohflpcr")
}
ARTIGO_REPEATABLE_RECORD_TYPES = {"p", "c", "r"}

ID_FUNCTIONS = {
    TITLE: id2json3.journal_id,
    ISSUE: id2json3.issue_id,
    ARTIGO: id2json3.article_id,
}

# campos de data por tipo de base
DATE_FIELDS = {
    TITLE: {"update": "v941", "processing": "v941", "creation": "v940"},
    ISSUE: {"update": "v091", "processing": "v091", "creation": "v093"},
    ARTIGO: {
        "update": "v091",
        "processing": "v091",
        "creation": "v093",
        "publication": "v065",
    },
}

# a data do item é o valor do campo no registro do grupo que o contém
# (em artigo, v091 está no registro "o", o primeiro do documento)


def normalize_db_type(db_type):
    try:
        return DB_TYPE_ALIASES[db_type.lower()]
    except (KeyError, AttributeError):
        raise ValueError(
            f"Invalid db_type={db_type}. Expected one of {sorted(DB_TYPE_ALIASES)}"
        )


def normalize_date(value, fill="0"):
    """
    Converte a data lida do registro (``item.date``) para string
    ``YYYYMMDD``. Valores incompletos são completados com ``fill``.
    Os filtros ``since``/``until`` usam ``filter_date``.
    """
    if value is None:
        return None
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime("%Y%m%d")
    digits = "".join(c for c in str(value) if c.isdigit())[:8]
    if not digits:
        return None
    return digits.ljust(8, fill)


def filter_date(value):
    """
    Valor de ``since``/``until`` como string ``YYYYMMDD``, o mesmo formato
    de ``item.date``. ``date``/``datetime`` são convertidos.
    """
    if value is None:
        return None
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime("%Y%m%d")
    return str(value)


def get_p_records_file_path(pid, base_paths):
    """
    Retorna o caminho do arquivo .id com os registros "p" (parágrafos) do
    artigo ``pid``, que ficam fora do arquivo principal, em
    ``{base}/artigo/p/{pid[1:10]}/{pid[10:14]}/{pid[14:18]}/{pid[-5:]}.id``.
    Procura em ``base_paths`` na ordem dada (ex.: [bases_work, bases]).
    Retorna None se não existir.
    """
    if not pid or len(pid) != 23 or not base_paths:
        return None
    partial_path = os.path.join(
        "artigo", "p", pid[1:10], pid[10:14], pid[14:18], pid[-5:] + ".id"
    )
    for base_path in base_paths:
        if not base_path:
            continue
        path = os.path.join(base_path, partial_path)
        if os.path.isfile(path):
            return path
    return None


def _parse_mfn(id_line):
    """``"!ID 0000123"`` -> 123"""
    try:
        return int(id_line[4:].strip())
    except (ValueError, TypeError):
        return None


def _parse_raw_records(raw_records):
    records = []
    for lines in raw_records:
        data = id2json3._build_record([id2json3._parse_field(line) for line in lines])
        if data:
            records.append(data)
    return records


def _extract_fields(lines, tags):
    """
    Decodifica apenas os campos ``tags`` (primeira ocorrência não vazia)
    das linhas de um registro. Retorna dict no mesmo formato de
    ``id2json3._build_record``, compatível com ``id2json3._get_value``.
    """
    data = {}
    for line in lines:
        pos = line.find("!", 1)
        tag = line[1:pos]
        if tag in tags and tag not in data:
            content = id2json3._parse_field_content(line[pos + 1 :])
            if content:
                data[tag] = [content]
    return data


class IdFileItem:
    """
    Item de um arquivo ``.id``: grupo de registros consecutivos com o mesmo PID.

    Para title e issue, normalmente um único registro.
    Para artigo, todos os registros do documento (o, h, f, l, p, r, c, ...)
    ou o registro "i" (issue) da base de artigos.

    Em artigo, se o documento não tem registros "p" no arquivo principal,
    ``records`` inclui os registros "p" do arquivo externo
    (ver ``get_p_records_file_path``), quando existir.
    """

    __slots__ = (
        "db_type",
        "pid",
        "date",
        "offset",
        "record_type",
        "record_types",
        "_kind",
        "_raw_records",
        "_records",
        "_main_records",
        "_p_base_paths",
        "_p_records_path",
        "_encoding",
        "mfn",
        "last_mfn",
    )

    def __init__(
        self,
        db_type,
        pid,
        date,
        offset,
        record_type,
        raw_records,
        p_base_paths=None,
        encoding="iso-8859-1",
        mfn=None,
        last_mfn=None,
        record_types=None,
    ):
        self.db_type = db_type
        # MFN do primeiro e do último registro do item (linha "!ID")
        self.mfn = mfn
        self.last_mfn = last_mfn
        self.pid = pid
        self.date = date
        self.offset = offset
        self.record_type = record_type
        # tipos (v706) dos registros do item no arquivo principal, em ordem
        self.record_types = tuple(record_types or ())
        self._kind = None
        self._raw_records = raw_records
        self._records = None
        self._main_records = None
        self._p_base_paths = p_base_paths
        self._p_records_path = False  # False = ainda não verificado
        self._encoding = encoding

    def __repr__(self):
        return (
            f"IdFileItem(db_type={self.db_type!r}, pid={self.pid!r}, "
            f"date={self.date!r}, kind={self.kind!r}, "
            f"n_records={len(self._raw_records)})"
        )

    @property
    def main_records(self):
        """Registros do arquivo principal em JSON (parse cacheado)"""
        if self._main_records is None:
            self._main_records = _parse_raw_records(self._raw_records)
        return self._main_records

    @property
    def has_main_p_records(self):
        return any(
            id2json3._get_value(record, "v706") == "p" for record in self.main_records
        )

    @property
    def external_p_records_path(self):
        """
        Caminho do arquivo externo de registros "p" do documento ou None.
        Só é consultado para documentos sem registros "p" no arquivo principal.
        """
        if self._p_records_path is False:
            path = None
            if (
                self.kind == "document"
                and self._p_base_paths
                and not self.has_main_p_records
            ):
                path = get_p_records_file_path(self.pid, self._p_base_paths)
            self._p_records_path = path
        return self._p_records_path

    @property
    def external_p_records(self):
        """Registros "p" do arquivo externo (lista vazia se não existir)"""
        path = self.external_p_records_path
        if not path:
            return []
        p_file = ClassicIdFile(ARTIGO, path, encoding=self._encoding)
        return [
            record
            for record in _parse_raw_records(
                lines for _, _, lines in p_file.iter_raw_records()
            )
            if id2json3._get_value(record, "v706") == "p"
        ]

    @property
    def records(self):
        """
        Lista de registros em JSON (parse completo e cacheado).
        Em artigo, inclui os registros "p" externos, se houver.
        """
        if self._records is None:
            records = list(self.main_records)
            if self.db_type == ARTIGO:
                if not self.has_main_p_records:
                    records.extend(self.external_p_records)
            self._records = records
        return self._records

    @property
    def p_records(self):
        """Registros "p" do documento (do arquivo principal ou externo)"""
        return [
            record
            for record in self.records
            if id2json3._get_value(record, "v706") == "p"
        ]

    @property
    def data(self):
        """Primeiro registro (útil para title e issue)"""
        records = self.records
        return records[0] if records else None

    @property
    def kind(self):
        """
        title -> "journal"; issue -> "issue";
        artigo -> "issue" (registro i), "document" ou "broken".

        Em artigo, é "document" o lote que começa com registro "o", tem
        registro "h" e PID de 23 caracteres. Qualquer outro lote é
        "broken" e não deve ser processado como documento.
        """
        if self._kind is None:
            self._kind = self._get_kind()
        return self._kind

    def _get_kind(self):
        if self.db_type == TITLE:
            return "journal"
        if self.db_type == ISSUE:
            return "issue"
        if self.record_type == "i":
            return "issue"
        if (
            self.record_type == "o"
            and "h" in self.record_types
            and self.pid
            and len(self.pid) == 23
        ):
            return "document"
        return "broken"

    @property
    def issue_pid(self):
        """PID do fascículo (17 caracteres sem o "S") para documentos"""
        if self.db_type == ARTIGO and self.kind == "document":
            return self.pid[1:18]
        if self.kind == "issue":
            return self.pid

    @property
    def date_as_date(self):
        """``self.date`` como ``datetime.date`` ou None se inválida/parcial"""
        try:
            return datetime.datetime.strptime(self.date, "%Y%m%d").date()
        except (TypeError, ValueError):
            return None


class ClassicIdFile:
    """
    Interface para um arquivo ``.id`` de base ISIS do site clássico.

    Parameters
    ----------
    db_type: str
        "title" (ou "journal"), "issue", "artigo" (ou "article")
    path: str
        caminho do arquivo ``.id``
    date_field: str
        campo usado como data do item: "update" (padrão), "processing",
        "creation", "publication" (somente artigo) ou uma tag ("v091")
    encoding: str
        codificação do arquivo (padrão iso-8859-1)
    p_records_base_paths: list of str
        somente artigo: diretórios onde procurar os arquivos externos de
        registros "p" (``{base}/artigo/p/...``), na ordem de prioridade,
        ex.: [bases_work_path, bases_path]. Se None, não procura.
    """

    def __init__(
        self,
        db_type,
        path,
        date_field="update",
        encoding="iso-8859-1",
        p_records_base_paths=None,
    ):
        self.db_type = normalize_db_type(db_type)
        self.path = path
        self.encoding = encoding
        self.date_field = date_field
        if isinstance(p_records_base_paths, str):
            p_records_base_paths = [p_records_base_paths]
        self.p_records_base_paths = p_records_base_paths
        self._index = None
        # posições (offset) dos lotes quebrados registradas na última
        # leitura completa e a "assinatura" do arquivo nessa leitura
        self._broken_offsets = None
        self._broken_offsets_signature = None

    def _file_signature(self):
        stat = os.stat(self.path)
        return stat.st_size, stat.st_mtime_ns

    def _known_broken_offsets(self):
        """
        Posições dos lotes quebrados, se registradas numa leitura completa
        e o arquivo não mudou desde então; caso contrário, None.
        """
        if self._broken_offsets is None:
            return None
        try:
            if self._file_signature() != self._broken_offsets_signature:
                return None
        except OSError:
            return None
        return self._broken_offsets

    def __repr__(self):
        return f"ClassicIdFile({self.db_type!r}, {self.path!r})"

    def __iter__(self):
        return self.items()

    def _date_tag(self, date_field):
        date_field = date_field or self.date_field
        fields = DATE_FIELDS[self.db_type]
        if date_field in fields:
            return fields[date_field]
        if date_field and date_field.startswith("v"):
            return "v" + date_field[1:].zfill(3)
        raise ValueError(
            f"Invalid date_field={date_field} for {self.db_type}. "
            f"Expected one of {sorted(fields)} or a tag (ex.: v091)"
        )

    # ------------------------------------------------------------------
    # leitura de baixo nível
    # ------------------------------------------------------------------
    def iter_raw_records(self, start=0):
        """
        Lê o arquivo linha a linha (sem carregá-lo em memória) e retorna
        ``(offset, mfn, lines)`` para cada registro, onde ``offset`` é a
        posição em bytes da linha ``!ID``, ``mfn`` é o número do registro
        (int) e ``lines`` são as linhas ``!vNNN!...``.

        Quebras de linha que fazem parte do conteúdo do campo são
        convertidas em um espaço simples: qualquer linha que não seja
        ``!ID <n>`` nem ``!v<tag>!...`` é continuação do campo anterior.
        """
        encoding = self.encoding
        with open(self.path, "rb") as fp:
            if start:
                fp.seek(start)
            offset = start
            record_offset = start
            mfn = None
            lines = []
            for raw in fp:
                line_offset = offset
                offset += len(raw)
                row = raw.decode(encoding).strip()
                if not row:
                    continue
                if "\r" in row:
                    row = " ".join(row.split("\r"))
                # caso mais frequente primeiro: linha de campo !v<tag>!
                if row.startswith("!v"):
                    end = row.find("!", 2)
                    if end > 2 and row[2:end].isdigit():
                        lines.append(row)
                        continue
                elif row.startswith("!ID ") and row[4:].strip().isdigit():
                    if lines:
                        yield record_offset, mfn, lines
                    lines = []
                    record_offset = line_offset
                    mfn = _parse_mfn(row)
                    continue
                if lines:
                    # quebra de linha dentro do conteúdo do campo -> espaço
                    lines[-1] = lines[-1].rstrip() + " " + row
            if lines:
                yield record_offset, mfn, lines

    def _iter_groups(self, date_tag, start=0, stop_after_first=False):
        """
        Retorna os itens do arquivo (``_read_groups``). Em artigo, numa
        leitura completa, registra a posição dos lotes quebrados (um inteiro
        por lote), para que ``broken_batches()`` os leia sem reler o arquivo.
        Se a leitura for interrompida, nada é registrado.
        """
        groups = self._read_groups(date_tag, start, stop_after_first)
        if self.db_type != ARTIGO or start or stop_after_first:
            yield from groups
            return
        signature = self._file_signature()
        broken_offsets = []
        for item in groups:
            if item.kind == "broken":
                broken_offsets.append(item.offset)
            yield item
        self._broken_offsets = broken_offsets
        self._broken_offsets_signature = signature

    def _read_groups(self, date_tag, start=0, stop_after_first=False):
        """
        Agrupa registros consecutivos com o mesmo PID e retorna ``IdFileItem``.

        Em artigo, os registros de um documento formam um lote que segue a
        ordem o, h, f, l, p, c, r (tipos podem faltar). Um novo lote começa
        quando a ordem se inverte (ex.: "o" ou "h" depois de "c"), quando um
        tipo que não se repete aparece de novo ou quando o PID muda. O registro "i" (registro do fascículo) não
        faz parte de nenhum documento: não interrompe nem integra o grupo
        do documento e é retornado como item próprio (kind="issue").
        Registros sem v706 (ex.: apenas ``v880=S`` e ``v936``) não pertencem
        a nenhum documento e são ignorados.
        """
        id_function = ID_FUNCTIONS[self.db_type]
        tags = set(ID_TAGS[self.db_type]) | {date_tag, "v706"}
        is_artigo = self.db_type == ARTIGO

        pending_issues = []

        item_id = None
        last_rank = None
        group_keys = []
        group_lines = []
        group_offset = start
        group_mfns = []

        for record_offset, mfn, lines in self.iter_raw_records(start):
            keys = _extract_fields(lines, tags)
            new_id = id_function(keys)

            if is_artigo:
                record_type = id2json3._get_value(keys, "v706")
                if not record_type:
                    continue

            if is_artigo and record_type == "i":
                issue_item = self._build_item(
                    new_id, record_offset, [keys], [lines], date_tag, [mfn]
                )
                if group_lines:
                    # não interrompe o documento em andamento
                    pending_issues.append(issue_item)
                else:
                    yield issue_item
                    if stop_after_first:
                        return
                continue

            # em artigo, novo lote quando a ordem dos tipos se inverte ou um
            # tipo que não se repete aparece de novo
            breaks_sequence = False
            rank = None
            if is_artigo:
                rank = ARTIGO_RECORD_TYPES_ORDER.get(record_type)
                if group_lines and rank is not None and last_rank is not None:
                    breaks_sequence = rank < last_rank or (
                        rank == last_rank
                        and record_type not in ARTIGO_REPEATABLE_RECORD_TYPES
                    )
            if breaks_sequence or (item_id and new_id != item_id):
                yield self._build_item(
                    item_id, group_offset, group_keys, group_lines, date_tag,
                    group_mfns,
                )
                if stop_after_first:
                    return
                yield from pending_issues
                pending_issues = []
                group_keys = []
                group_lines = []
                group_mfns = []
                last_rank = None
            if rank is not None:
                last_rank = rank
            if not group_lines:
                group_offset = record_offset
            item_id = new_id
            group_keys.append(keys)
            group_lines.append(lines)
            group_mfns.append(mfn)

        if group_lines:
            yield self._build_item(
                item_id, group_offset, group_keys, group_lines, date_tag,
                group_mfns,
            )
        if not stop_after_first:
            yield from pending_issues

    def _build_item(self, pid, offset, group_keys, group_lines, date_tag, mfns):
        record_type = id2json3._get_value(group_keys[0], "v706")
        date = None
        for keys in group_keys:
            date = id2json3._get_value(keys, date_tag)
            if date:
                break
        return IdFileItem(
            self.db_type,
            pid,
            normalize_date(date),
            offset,
            record_type,
            group_lines,
            p_base_paths=self.p_records_base_paths if self.db_type == ARTIGO else None,
            encoding=self.encoding,
            mfn=mfns[0] if mfns else None,
            last_mfn=mfns[-1] if mfns else None,
            record_types=[id2json3._get_value(keys, "v706") for keys in group_keys],
        )

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def items(
        self,
        since=None,
        until=None,
        pids=None,
        kind=None,
        include_undated=False,
        date_field=None,
    ):
        """
        Retorna os itens bons (``IdFileItem`` com ``pid``, ``date`` e
        ``records`` lazy): em artigo, documentos e registros de fascículo.
        Os lotes quebrados (kind="broken") não são retornados; para
        auditoria, use ``broken_batches()``.

        Parameters
        ----------
        since, until: str | date | datetime
            intervalo de datas (inclusivo), str com 8 dígitos ``YYYYMMDD``
            (ex.: "20240315"), ``date`` ou ``datetime``
        pids: iterable of str
            retorna somente estes PIDs
        kind: str | iterable of str
            filtra por ``item.kind`` ("document", "issue", "journal");
            útil para artigo
        include_undated: bool
            ao filtrar por data, inclui itens sem data
        date_field: str
            sobrescreve ``self.date_field`` nesta chamada
        """
        if isinstance(kind, str):
            kind = {kind}
        elif kind is not None:
            kind = set(kind)
        match = self._matcher(since, until, pids, include_undated)
        for item in self._iter_groups(self._date_tag(date_field)):
            item_kind = item.kind
            if item_kind == "broken":
                continue
            if kind is not None and item_kind not in kind:
                continue
            if match(item):
                yield item

    def broken_batches(self):
        """
        Todos os lotes de registros de artigo que não formam um documento
        (kind="broken"), ex.: registro "o" sem "h", registros "h", "f"...
        sem "o". Ficam separados de ``items()`` para auditoria: não devem
        ser processados como documentos e não são filtrados (os filtros
        são de ``items()``). ``item.record_types``, ``item.mfn``,
        ``item.last_mfn`` e ``item.offset`` os localizam no arquivo.

        Se o arquivo já foi lido por completo (``items()``, ``build_index()``
        ...) e não mudou, lê somente os lotes quebrados, a partir das
        posições registradas, sem reler o arquivo.
        """
        if self.db_type != ARTIGO:
            return
        date_tag = self._date_tag(None)
        offsets = self._known_broken_offsets()
        if offsets is None:
            for item in self._iter_groups(date_tag):
                if item.kind == "broken":
                    yield item
        else:
            yield from self._read_batches_at(offsets, date_tag)

    def _read_batches_at(self, offsets, date_tag):
        for offset in offsets:
            for item in self._read_groups(
                date_tag, start=offset, stop_after_first=True
            ):
                yield item

    def _matcher(self, since, until, pids, include_undated):
        """Retorna a função que aplica os filtros de PID e de data"""
        since = filter_date(since)
        until = filter_date(until)
        if pids is not None:
            pids = set(pids)

        def match(item):
            if pids is not None and item.pid not in pids:
                return False
            if since or until:
                if not item.date:
                    return include_undated
                # inclusivo: since <= item.date <= until (YYYYMMDD)
                if since and item.date < since:
                    return False
                if until and item.date > until:
                    return False
            return True

        return match

    def pids(self, **filters):
        """Retorna somente os PIDs (sem parse completo dos registros)"""
        for item in self.items(**filters):
            yield item.pid

    def pids_and_dates(self, **filters):
        """Retorna ``(pid, date)`` (sem parse completo dos registros)"""
        for item in self.items(**filters):
            yield item.pid, item.date

    def pids_and_records(self, **filters):
        """
        Retorna ``(pid, records)``, compatível com
        ``id2json3.pids_and_their_records``
        """
        for item in self.items(**filters):
            yield item.pid, item.records

    def pids_dates_and_records(self, **filters):
        """Retorna ``(pid, date, records)``"""
        for item in self.items(**filters):
            yield item.pid, item.date, item.records

    def build_index(self, date_field=None):
        """
        Percorre o arquivo uma vez (parse mínimo) e guarda
        ``{pid: (offset, date)}``. Depois disso, ``get(pid)`` acessa o item
        diretamente via ``seek``, sem reler o arquivo inteiro.
        Se um PID aparece mais de uma vez, vale a última ocorrência
        (a mais recente, pois registros novos são adicionados ao final).
        Lotes quebrados não entram no índice.
        """
        index = {}
        for item in self.items(date_field=date_field):
            index[item.pid] = (item.offset, item.date)
        self._index = index
        return index

    @property
    def index(self):
        return self._index

    def get(self, pid, date_field=None):
        """
        Retorna o ``IdFileItem`` de ``pid`` ou None (somente itens bons;
        lotes quebrados são ignorados).
        Se o PID aparece mais de uma vez, retorna a última ocorrência.
        Usa o índice se ``build_index()`` tiver sido chamado; caso contrário,
        lê o arquivo inteiro (para várias consultas, use ``build_index()``).
        """
        date_tag = self._date_tag(date_field)
        if self._index is not None:
            found = self._index.get(pid)
            if not found:
                return None
            for item in self._iter_groups(
                date_tag, start=found[0], stop_after_first=True
            ):
                return item
            return None
        found = None
        for item in self.items(pids=[pid], date_field=date_field):
            found = item
        return found

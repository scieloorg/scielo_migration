"""
Identifica, no início do body, o texto da página de rosto.

Os registros de parágrafo (tipo p) trazem o texto completo do artigo, sem
rótulos: página de rosto (título, autores, afiliações, resumos,
palavras-chave, histórico), corpo e anexos. Sem uma seção de introdução
reconhecida, a página de rosto fica no body e aparece duas vezes no
artigo (front e body).

Os blocos do início do body são comparados com os metadados do artigo
(registro h): um bloco é da página de rosto se o seu texto está nos
metadados (``STRONG``) ou se é uma linha do histórico ("Recebido: ...",
"Aceito: ...") ou rotulada com conteúdo em parte nos metadados
("Palavras-chave: ...") (``WEAK``); um rótulo sozinho ("Resumo") acompanha o bloco
seguinte (``NEUTRAL``). Remove-se do início do
body até o último bloco da página de rosto, desde que haja ao menos um
bloco confirmado pelos metadados. O primeiro bloco que não é da página de
rosto encerra a busca: o que não está nos metadados (ex.: resumo não
cadastrado) permanece no body, sem perda de conteúdo.
"""

import re
import unicodedata

STRONG = "strong"
WEAK = "weak"
NEUTRAL = "neutral"

CHUNK = 40  # letras: trecho dos blocos longos procurado nos metadados
LONG_BLOCK = 150  # letras: acima disso, compara por trechos
MIN_CHUNK_COVERAGE = 0.6
MIN_WORD_COVERAGE = 0.75
MIN_LONG_WORD_COVERAGE = 0.9
# linha rotulada ("Palavras-chave: ..."), com grafia diferente da cadastrada
MIN_LABELED_WORD_COVERAGE = 0.5
MAX_HEADING_WORDS = 6
MIN_TITLE_PART = 10  # letras
MIN_PREFIX = 6  # letras
MIN_PREFIX_RATIO = 0.75
MIN_WORD = 3  # letras: palavras menores são ignoradas na comparação
MIN_WORDS = 4  # palavras: menos que isso, o bloco é comparado com itens inteiros

# rótulos da página de rosto (comparados sem acentos, em minúsculas)
CONTENT_LABELS = (
    "resumo", "resumen", "abstract", "resume", "summary", "sumario", "sinopsis",
    "palavras chave", "palavras-chave", "palabras clave", "palabras-clave",
    "key words", "keywords", "key-words", "keyt word", "keyt words", "keyword",
    "descritores", "descriptores", "descriptors", "unitermos", "mots cles", "mots-cles",
)
# histórico e correspondência: linha da página de rosto mesmo sem estar nos
# metadados
HISTORY_LABELS = (
    "recebido", "recibido", "received", "aceito", "aceptado", "accepted",
    "aprovado", "aprobado", "approved", "submetido", "submitted",
    "endereco para correspondencia", "direccion para correspondencia",
    "correspondencia", "correspondence",
)


def _label_re(labels):
    return re.compile(r"^\W*(" + "|".join(re.escape(label) for label in labels) + r")\b\W*")


_LABEL_RE = _label_re(CONTENT_LABELS + HISTORY_LABELS)
_LABEL_SEPARATOR_RE = re.compile(r"[:.]")
_HISTORY_RE = _label_re(HISTORY_LABELS)
_LETTERS_RE = re.compile(r"[^\W\d_]+")
_TAG_RE = re.compile(r"<[^>]+>")

def _plain(text):
    """Minúsculas e sem acentos."""
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def _words(text):
    return _LETTERS_RE.findall(_plain(text))


def _letters(text):
    return "".join(_words(text))


def _alnum(text):
    """Letras e dígitos (ex.: "Caso clínico #1" difere de "Caso clínico")."""
    return "".join(re.findall(r"[^\W_]+", _plain(_TAG_RE.sub(" ", text or ""))))


def _matches_item(value, items):
    """Igual a um item ou o seu início (ex.: "Original" e "Originales")."""
    if not value:
        return False
    if value in items:
        return True
    return len(value) >= MIN_PREFIX and any(
        item.startswith(value) and len(value) >= MIN_PREFIX_RATIO * len(item) for item in items
    )


class FrontMetadata:
    """Textos da página de rosto registrados nos metadados do artigo."""

    def __init__(self, texts, items=None, titles=None, sections=None):
        """
        ``texts``: todos os textos (títulos, resumos, palavras-chave,
        autores, afiliações, seção); ``items``: os que podem ser uma linha
        inteira do body (títulos, autores, afiliações, seção), para
        comparar os blocos curtos; ``titles``: títulos do artigo, que no
        HTML podem estar quebrados em várias linhas; ``sections``: seção do
        sumário, que só é procurada antes do título (depois, uma linha igual
        é um subtítulo, como "Caso clínico").
        """
        texts = [_TAG_RE.sub(" ", t) for t in texts if t and isinstance(t, str)]
        # "|" separa os textos: um trecho não é encontrado entre dois deles
        self.letters = "|".join(_letters(t) for t in texts)
        self.words = {w for t in texts for w in _words(t) if len(w) >= MIN_WORD}
        self.items = {_letters(_TAG_RE.sub(" ", t)) for t in (items or []) if t and isinstance(t, str)}
        self.items.discard("")
        self.sections = {_alnum(t) for t in (sections or []) if t and isinstance(t, str)}
        self.sections.discard("")
        self.titles = "|".join(_letters(_TAG_RE.sub(" ", t)) for t in (titles or []) if t and isinstance(t, str))

    def __bool__(self):
        return bool(self.words or self.sections)

    @classmethod
    def from_document(cls, document):
        """Títulos, resumos, palavras-chave, autores, afiliações e seção."""
        h_record = getattr(document, "h_record", None)
        if h_record is None:
            return cls([])
        items = []
        texts = []

        def values(name):
            try:
                return getattr(h_record, name) or []
            except Exception:
                return []

        titles = []
        for item in values("article_titles"):
            items += [item.get("text"), item.get("subtitle")]
            titles.append(" ".join(filter(None, [item.get("text"), item.get("subtitle")])))
        items += titles
        for item in values("authors"):
            items.append(" ".join(filter(None, [item.get("given_names"), item.get("surname")])))
        items += [t for t in values("corporative_authors") if isinstance(t, str)]
        for item in values("affiliations"):
            items += [v for k, v in item.items() if k not in ("id", "email") and isinstance(v, str)]
        sections = []
        try:
            # seção do sumário (ex.: "COMUNICAÇÕES BREVES"), em todos os idiomas
            sections = [item.get("text") for item in document.get_sections().values()]
        except Exception:
            pass
        for item in values("abstracts"):
            texts.append(item.get("text"))
        for item in values("keywords"):
            texts += [item.get("text"), item.get("subkey")]
        return cls(texts + items, items, titles, sections)

    def chunk_positions(self, text):
        """Posição, nos metadados, de cada trecho encontrado do bloco."""
        letters = _letters(text)
        positions = []
        for i in range(0, len(letters) - CHUNK + 1, CHUNK):
            pos = self.letters.find(letters[i:i + CHUNK])
            if pos >= 0:
                positions.append(pos)
        return positions

    def is_section(self, text):
        """Linha da seção do sumário (ex.: "Original", seção "Originales")."""
        return _matches_item(_alnum(text), self.sections)

    def is_item(self, letters):
        """Igual a um item ou o seu início (ex.: "Original", seção "Originales")."""
        return _matches_item(letters, self.items)

    def is_title_part(self, text):
        """Linha de um título quebrado em várias linhas."""
        letters = _letters(text)
        return len(letters) >= MIN_TITLE_PART and letters in self.titles

    def word_coverage(self, text, min_words=MIN_WORDS):
        words = [w for w in _words(text) if len(w) >= MIN_WORD]
        if not words or len(words) < min_words:
            return 0
        return sum(1 for w in words if w in self.words) / len(words)

    def contains(self, text):
        """O texto (bloco do body) está nos metadados?"""
        letters = _letters(text)
        if not letters:
            return False
        if len(letters) > LONG_BLOCK:
            chunks = [letters[i:i + CHUNK] for i in range(0, len(letters) - CHUNK + 1, CHUNK)]
            found = sum(1 for chunk in chunks if chunk in self.letters)
            if found / len(chunks) >= MIN_CHUNK_COVERAGE:
                return True
            # lista longa (ex.: autores), cujos itens estão separados nos metadados
            return self.word_coverage(text) >= MIN_LONG_WORD_COVERAGE
        if len([w for w in _words(text) if len(w) >= MIN_WORD]) < MIN_WORDS:
            # bloco curto: igual a um item (título, autor, seção...), e não um
            # subtítulo do body que aparece no resumo ou nas palavras-chave
            return self.is_item(letters)
        if letters in self.letters:
            return True
        return self.word_coverage(text) >= MIN_WORD_COVERAGE


def _is_heading(text):
    words = _LETTERS_RE.findall(text or "")
    return 0 < len(words) <= MAX_HEADING_WORDS and all(w.isupper() for w in words)


def classify(node, metadata):
    """STRONG, WEAK, NEUTRAL ou None (não é da página de rosto)."""
    text = " ".join(node.itertext())
    if not _letters(text):
        return NEUTRAL
    plain = " ".join(_plain(text).split())
    label = _LABEL_RE.match(plain)
    rest = plain[label.end():] if label else plain
    if label and not _letters(rest):
        # só o rótulo (ex.: "Resumo"): depende do bloco seguinte
        return NEUTRAL
    if _is_heading(text):
        # linha curta em maiúsculas (ex.: seção do sumário, "COMUNICAÇÕES
        # BREVES"): depende do bloco seguinte
        return NEUTRAL if not metadata.contains(rest) else STRONG
    if metadata.contains(rest):
        return STRONG
    if _HISTORY_RE.match(plain):
        return WEAK
    if (
        label
        and _LABEL_SEPARATOR_RE.search(plain[label.start(1) : label.end()])
        and metadata.word_coverage(rest, min_words=1) >= MIN_LABELED_WORD_COVERAGE
    ):
        # "Palavras-chave: ...", não um subtítulo como "Resumen del caso:"
        return WEAK
    # rótulo com conteúdo que não está nos metadados (ex.: palavras-chave
    # não cadastradas): permanece no body
    return None


# contêineres: nunca classificados como um todo (ex.: a primeira seção pode
# conter a página de rosto e a introdução); os seus blocos são avaliados
CONTAINERS = ("sec", "abstract", "trans-abstract", "kwd-group", "div", "body")


def _is_container(node):
    return node.tag in CONTAINERS and any(isinstance(child.tag, str) for child in node)


def _leaves(node):
    """Blocos (folhas) em ordem, descendo nos contêineres."""
    for child in node:
        if not isinstance(child.tag, str):
            continue
        if _is_container(child):
            yield from _leaves(child)
        else:
            yield child


def _remove(nodes, body):
    """Remove os blocos e os contêineres que ficaram vazios."""
    for node in nodes:
        parent = node.getparent()
        parent.remove(node)
        while parent is not body and not len(parent) and not "".join(parent.itertext()).strip():
            grandparent = parent.getparent()
            grandparent.remove(parent)
            parent = grandparent


def _consume(metadata, text, used):
    """
    Marca como usados os trechos dos metadados encontrados no bloco longo.
    Falso se a maioria já tinha sido usada por um bloco anterior.
    """
    if len(_letters(text)) <= LONG_BLOCK:
        return True
    positions = metadata.chunk_positions(text)
    if not positions:
        return True
    repeated = sum(1 for pos in positions if used[pos] or used[pos + CHUNK - 1])
    if repeated / len(positions) >= 0.5:
        return False
    for pos in positions:
        used[pos : pos + CHUNK] = b"\x01" * CHUNK
    return True


def strip_front_text(body, metadata):
    """
    Remove do início do body os blocos da página de rosto. Retorna os
    blocos removidos.
    """
    if not metadata:
        return []
    leaves = list(_leaves(body))
    last_front = None
    has_strong = False
    at_title = True  # ainda no início: o título pode estar quebrado em linhas
    used = bytearray(len(metadata.letters))  # trechos dos metadados já usados
    for i, leaf in enumerate(leaves):
        text = " ".join(leaf.itertext())
        if last_front is None and metadata.is_section(text):
            kind = STRONG
        elif at_title and metadata.is_title_part(text):
            kind = STRONG
        else:
            kind = classify(leaf, metadata)
            if kind != NEUTRAL:
                at_title = False
        if kind == STRONG and not _consume(metadata, text, used):
            # repete um trecho já encontrado (ex.: quadro ou conclusão que
            # reproduz o resumo): é do body
            kind = None
        if kind is None:
            break
        if kind == STRONG:
            has_strong = True
        if kind in (STRONG, WEAK):
            last_front = i
    if last_front is None or not has_strong or last_front + 1 >= len(leaves):
        # nada a remover, ou o body ficaria vazio
        return []
    removed = leaves[: last_front + 1]
    _remove(removed, body)
    return removed


def strip_trailing_front_text(body, metadata):
    """
    Remove do fim do body a página de rosto (ex.: resumo em outro idioma
    depois da discussão): do rótulo ("Abstract") até o fim, desde que haja
    um resumo (bloco longo) e só blocos da página de rosto. Sem o rótulo,
    nada é removido: a conclusão costuma repetir frases do resumo.
    Retorna os blocos removidos.
    """
    if not metadata:
        return []
    leaves = list(_leaves(body))
    start = None
    has_strong = False
    for i in range(len(leaves) - 1, -1, -1):
        leaf = leaves[i]
        kind = classify(leaf, metadata)
        if kind is None:
            break
        if kind == STRONG and len(_letters(" ".join(leaf.itertext()))) > LONG_BLOCK:
            has_strong = True
        if kind == NEUTRAL and _letters(" ".join(leaf.itertext())):
            # rótulo ("Abstract"): início da página de rosto no fim do body
            if has_strong:
                start = i
            break
    if start is None or start == 0:
        # sem rótulo, o bloco pode ser a conclusão, que repete o resumo
        return []
    removed = leaves[start:]
    _remove(removed, body)
    return removed

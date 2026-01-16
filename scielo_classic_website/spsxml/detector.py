import re
from typing import Dict, Optional, Tuple, List
import unicodedata

# Importações dos módulos de configuração
from scielo_classic_website.spsxml.detector_config_xref import (
    REF_TYPE_TO_ELEMENT,
    ID_PATTERNS,
    TEXT_PATTERNS,
    REF_TYPE_TO_ID_PREFIX,
)
from scielo_classic_website.spsxml.detector_config_sec import (
    SEC_TYPE_PATTERNS,
    COMBINED_PATTERNS,
    REFERENCIAS_PATTERNS,
    AGRADECIMENTOS_PATTERNS,
)
from scielo_classic_website.spsxml.detector_config_fn import (
    FN_TYPE_PATTERNS,
    SYMBOL_TO_FN_TYPE,
    FN_NUMBER_PATTERNS,
    NOT_FN_INDICATORS,
)


def detect_from_id(rid: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Detecta ref-type e element-name a partir de um ID no padrão estabelecido.

    Args:
        rid: ID no formato padrão (ex: f1, t2, B3, sec4_1)

    Returns:
        Tupla (ref_type, element_name) ou (None, None)

    Exemplos:
        >>> detect_from_id("f1")
        ('fig', 'fig')
        >>> detect_from_id("B42")
        ('bibr', 'ref')
        >>> detect_from_id("sec2_1")
        ('sec', 'sec')
    """
    if not rid:
        return None, None

    # Tenta identificar pelo padrão do ID
    for pattern, ref_type in ID_PATTERNS.items():
        if re.match(pattern, rid, re.IGNORECASE):
            element_name = REF_TYPE_TO_ELEMENT.get(ref_type)
            return ref_type, element_name

    return None, None


def detect_from_text(
    text: str, context: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Detecta ref-type, element-name e gera RID a partir do texto.

    Args:
        text: Texto da referência (ex: "Fig. 1", "Tabla 2")
        context: Contexto adicional opcional

    Returns:
        Tupla (ref_type, element_name, prefix, number) ou (None, None, None, None)

    Exemplos:
        >>> detect_from_text("Figure 1")
        ('fig', 'fig', 'f', '1')
        >>> detect_from_text("Tableau 3")
        ('table', 'table-wrap', 't', '3')
    """
    if not text:
        return None, None, None, None

    text = text.strip()
    if not text:
        return None, None, None, None

    # Verifica padrões de texto
    for ref_type, patterns in TEXT_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, text):
                element_name = REF_TYPE_TO_ELEMENT.get(ref_type)
                prefix, number = get_id_prefix_and_number(text, ref_type)
                return ref_type, element_name, prefix, number

    return None, None, None, None


def get_id_prefix_and_number(text: str, ref_type: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Gera um ID apropriado a partir do texto da referência.

    Args:
        text: Texto da referência
        ref_type: Tipo já identificado (opcional)

    Returns:
        Tupla (prefix, number)
    """
    prefix = None
    number = None

    if text:
        text = text.strip()
        # Extrai número do texto
        number = extract_number_from_text(text)

    if ref_type:
        # Obtém o prefixo apropriado
        prefix = REF_TYPE_TO_ID_PREFIX.get(ref_type, ref_type)

    return prefix, number


def extract_number_from_text(text: str) -> Optional[str]:
    """
    Extrai número ou identificador de um texto.
    """
    text = text.strip()
    if not text:
        return None

    if text.isdigit():
        return text

    patterns = [
        r"(\d+[A-Za-z]?)",  # Números com possível letra
        r"\[(\d+)\]",  # Entre colchetes
        r"\((\d+)\)",  # Entre parênteses
        r"([A-Z])(?:\s|$)",  # Letra maiúscula (apêndices)
        r"([a-z])(?:\s|$)",  # Letra minúscula (notas)
        r"(\d+\.\d+)",  # Números hierárquicos
        r"([*†‡§¶#]+)",  # Símbolos especiais
        r"S(\d+)",  # Material suplementar
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None


def analyze_xref(text: str = None, rid: str = None) -> Dict[str, Optional[str]]:
    """
    Função principal que analisa uma referência cruzada.
    Pode receber texto, ID, ou ambos.

    Args:
        text: Texto da referência (opcional)
        rid: ID da referência (opcional)

    Returns:
        Dicionário com ref_type, element_name, rid e outras informações

    Exemplos:
        >>> analyze_xref(text="Figure 1")
        {'ref_type': 'fig', 'element_name': 'fig', 'rid': 'f1', 'source': 'text'}

        >>> analyze_xref(rid="t3")
        {'ref_type': 'table', 'element_name': 'table-wrap', 'rid': 't3', 'source': 'id'}

        >>> analyze_xref(text="Tabla 2", rid="t2")
        {'ref_type': 'table', 'element_name': 'table-wrap', 'rid': 't2', 'source': 'both', 'consistent': True}
    """
    result = {
        "ref_type": None,
        "element_name": None,
        "prefix": None,
        "number": None,
        "rid": None,
        "source": None,
        "consistent": None,
    }

    prefix = None
    number = None
    ref_type_text = None
    element_name_text = None

    # Análise do texto
    if text:
        ref_type_text, element_name_text, prefix, number = detect_from_text(text)
        if ref_type_text:
            result["ref_type"] = ref_type_text
            result["element_name"] = element_name_text
            result["prefix"] = prefix
            result["number"] = number
            result["source"] = "text"
        else:
            ref_type_text, element_name_text, prefix, number = detect_from_text(text.split()[0])
            if ref_type_text:
                result["ref_type"] = ref_type_text
                result["element_name"] = element_name_text
                result["prefix"] = prefix
                result["number"] = number
                result["source"] = "text"


    # Análise do ID
    if rid:
        ref_type_id, element_name_id = detect_from_id(rid)
        if ref_type_id:
            if result["ref_type"]:
                # Tem ambos, verifica consistência
                result["consistent"] = (
                    ref_type_text == ref_type_id
                    and element_name_text == element_name_id
                )
                # Prefere o RID fornecido se consistente
                if result["consistent"]:
                    result["rid"] = rid
                    result["source"] = "both"
            else:
                # Só tem ID
                result["ref_type"] = ref_type_id
                result["element_name"] = element_name_id
                result["rid"] = rid
                result["source"] = "id"

    return result


def normalize_id(id_string: str) -> str:
    """
    Normaliza um ID para ser válido em XML.
    """
    # Remove acentos
    normalized = unicodedata.normalize("NFKD", id_string)
    normalized = "".join([c for c in normalized if not unicodedata.combining(c)])

    # Remove caracteres inválidos
    normalized = re.sub(r"[^a-zA-Z0-9_\-\.]", "", normalized)

    # Garante que comece com letra ou underscore
    if normalized and not re.match(r"^[a-zA-Z_]", normalized):
        normalized = "_" + normalized

    return normalized or "id1"


def batch_analyze_xrefs(xrefs: List[Dict[str, str]]) -> List[Dict[str, Optional[str]]]:
    """
    Analisa múltiplas referências cruzadas em lote.

    Args:
        xrefs: Lista de dicionários com 'text' e/ou 'rid'

    Returns:
        Lista de resultados da análise

    Exemplo:
        >>> batch_analyze_xrefs([
        ...     {'text': 'Fig. 1'},
        ...     {'rid': 'B2'},
        ...     {'text': 'Tabla 3', 'rid': 't3'}
        ... ])
    """
    results = []
    for xref in xrefs:
        result = analyze_xref(text=xref.get("text"), rid=xref.get("rid"))
        results.append(result)
    return results


def detect_sec_type(section_title: str) -> Optional[str]:
    """
    Detecta o tipo de seção (@sec-type) a partir do título da seção.
    Pode retornar múltiplos tipos concatenados com | para seções combinadas.

    Args:
        section_title: Título da seção em qualquer idioma suportado

    Returns:
        sec-type identificado (pode ser múltiplo com |) ou None se não identificado

    Exemplos:
        >>> detect_sec_type("Introduction")
        'intro'
        >>> detect_sec_type("Results and Discussion")
        'results|discussion'
        >>> detect_sec_type("Materials and Methods")
        'materials|methods'
        >>> detect_sec_type("Conclusions")
        'conclusions'
    """
    if not section_title:
        return None

    # Normaliza o título
    title = section_title.strip()
    title_lower = title.lower()

    # Primeiro, verifica combinações comuns que devem retornar tipos múltiplos

    # Verifica padrões combinados
    for pattern, sec_types in COMBINED_PATTERNS:
        if re.search(pattern, title_lower):
            return "|".join(sec_types)

    # Se não é uma combinação, tenta identificar tipos individuais
    detected_types = []

    # Palavras conectoras que indicam seções múltiplas
    connectors = r"\s+(and|&|e|y|et|und|en|com|avec|mit|met)\s+"

    # Verifica se tem conectores
    if re.search(connectors, title_lower):
        # Divide o título pelos conectores
        parts = re.split(connectors, title_lower)

        # Tenta detectar tipo para cada parte
        for part in parts:
            if part.strip() and part.strip() not in [
                "and",
                "&",
                "e",
                "y",
                "et",
                "und",
                "en",
                "com",
                "avec",
                "mit",
                "met",
            ]:
                for sec_type, patterns in SEC_TYPE_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern.replace("^", ""), part.strip()):
                            if sec_type not in detected_types:
                                detected_types.append(sec_type)
                            break

    # Se detectou múltiplos tipos através da divisão
    if len(detected_types) > 1:
        return "|".join(detected_types)

    # Caso contrário, tenta detecção simples
    for sec_type, patterns in SEC_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, title):
                return sec_type

    return None


def detect_sec_type_and_number(
    section_text: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Detecta o tipo de seção e extrai o número da seção.

    Args:
        section_text: Texto completo da seção (ex: "2.1 Metodologia")

    Returns:
        Tupla (sec_type, section_number)

    Exemplos:
        >>> detect_sec_type_and_number("2.1 Introduction")
        ('intro', '2.1')
        >>> detect_sec_type_and_number("3. Resultados")
        ('results', '3')
        >>> detect_sec_type_and_number("Materials and Methods")
        ('methods', None)
    """
    if not section_text:
        return None, None

    text = section_text.strip()

    # Padrões para extrair número de seção
    number_patterns = [
        r"^(\d+(?:\.\d+)*)\s*\.?\s+",  # 2.1 ou 2.1.
        r"^(\d+)\s*\.\s+",  # 3.
        r"^(\d+)\s+",  # 3
        r"^([A-Z])\s*\.\s+",  # A.
        r"^([A-Z])\s+",  # A
        r"^([IVX]+)\s*\.\s+",  # IV. (números romanos)
        r"^([IVX]+)\s+",  # IV
    ]

    section_number = None
    title_without_number = text

    # Tenta extrair o número
    for pattern in number_patterns:
        match = re.match(pattern, text)
        if match:
            section_number = match.group(1)
            title_without_number = text[match.end() :].strip()
            break

    # Detecta o tipo
    sec_type = detect_sec_type(title_without_number)

    return sec_type, section_number


def suggest_sec_id(section_title: str, default_number: str = "1") -> str:
    """
    Sugere um ID para uma seção baseado no título e tipo detectado.

    Args:
        section_title: Título da seção
        default_number: Número padrão se não detectado no título

    Returns:
        ID sugerido para a seção

    Exemplos:
        >>> suggest_sec_id("2.1 Introduction")
        'sec2_1'
        >>> suggest_sec_id("Materials and Methods", "3")
        'sec3'
        >>> suggest_sec_id("Conclusiones")
        'sec1'
    """
    sec_type, number = detect_sec_type_and_number(section_title)

    # Se detectou um número, usa ele
    if number:
        # Converte pontos em underscore para IDs válidos
        number = number.replace(".", "_")
    else:
        number = default_number

    return f"sec{number}"


def batch_detect_sec_types(section_titles: List[str]) -> List[Dict[str, Optional[str]]]:
    """
    Detecta tipos de múltiplas seções em lote.

    Args:
        section_titles: Lista de títulos de seções

    Returns:
        Lista de dicionários com sec_type, number e suggested_id

    Exemplo:
        >>> batch_detect_sec_types([
        ...     "1. Introduction",
        ...     "2. Materials and Methods",
        ...     "3. Results",
        ...     "4. Discussion"
        ... ])
    """
    results = []
    for i, title in enumerate(section_titles, 1):
        sec_type, number = detect_sec_type_and_number(title)
        suggested_id = suggest_sec_id(title, str(i))

        results.append(
            {
                "title": title,
                "sec_type": sec_type,
                "number": number,
                "suggested_id": suggested_id,
            }
        )

    return results


def detect_fn_type(title: str) -> Optional[str]:
    """
    Detecta o tipo de footnote (@fn-type) a partir do título ou texto.

    Args:
        title: Título ou texto da nota de rodapé

    Returns:
        fn-type identificado ou None se não identificado

    Exemplos:
        >>> detect_fn_type("Corresponding author")
        'corresp'
        >>> detect_fn_type("Financial disclosure")
        'financial-disclosure'
        >>> detect_fn_type("†These authors contributed equally")
        'equal'
    """
    if not title:
        return None

    title = title.strip()
    
    # Primeiro verifica se há símbolos especiais no início
    for symbol, fn_type in SYMBOL_TO_FN_TYPE.items():
        if title.startswith(symbol):
            # Se o símbolo sugere um tipo, ainda verifica o texto
            # para confirmar ou refinar a detecção
            title_without_symbol = title[len(symbol):].strip()
            detected_type = _detect_fn_type_from_patterns(title_without_symbol)
            if detected_type:
                return detected_type
            # Se não encontrou padrão específico, usa o tipo do símbolo
            return fn_type

    # Tenta detecção pelos padrões de texto
    return _detect_fn_type_from_patterns(title)


def _detect_fn_type_from_patterns(text: str) -> Optional[str]:
    """
    Função auxiliar para detectar fn-type a partir dos padrões de texto.
    """
    if not text:
        return None

    # Remove possível numeração do início
    clean_text = text
    for pattern in FN_NUMBER_PATTERNS:
        clean_text = re.sub(pattern, "", text, count=1)
        if clean_text != text:
            break

    clean_text = clean_text.strip()
    if not clean_text:
        return None

    # Verifica padrões de fn-type
    for fn_type, patterns in FN_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, clean_text):
                return fn_type

    return None


def detect_element_type(title: str, context: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Detecta se um título corresponde a uma seção (sec) ou footnote (fn).
    
    Args:
        title: Título ou texto a ser analisado
        context: Contexto adicional opcional (por ex: "back", "body", "front")
    
    Returns:
        Dicionário com:
        - element_type: 'sec', 'fn' ou None
        - type_attribute: sec-type ou fn-type detectado
        - confidence: 'high', 'medium', 'low'
        - detected_as: descrição do que foi detectado
        - suggested_id: ID sugerido para o elemento
    
    Exemplos:
        >>> detect_element_type("Introduction")
        {'element_type': 'sec', 'type_attribute': 'intro', ...}
        
        >>> detect_element_type("*Corresponding author")
        {'element_type': 'fn', 'type_attribute': 'corresp', ...}
        
        >>> detect_element_type("Financial disclosure: This work was supported by...")
        {'element_type': 'fn', 'type_attribute': 'financial-disclosure', ...}
    """
    result = {
        "element_type": None,
        "type_attribute": None,
        "confidence": None,
        "detected_as": None,
        "suggested_id": None,
        "number": None,
    }
    
    if not title:
        return result
    
    title = title.strip()
    if not title:
        return result
    
    for pattern in REFERENCIAS_PATTERNS:
        if re.search(pattern, title):
            result["element_type"] = "ref-list"
            return result
    
    for pattern in AGRADECIMENTOS_PATTERNS:
        if re.search(pattern, title):
            result["element_type"] = "ack"
            return result

    # Verifica se definitivamente NÃO é uma footnote
    for pattern in NOT_FN_INDICATORS:
        if re.match(pattern, title):
            # É uma seção
            sec_type, number = detect_sec_type_and_number(title)
            if sec_type:
                result["element_type"] = "sec"
                result["type_attribute"] = sec_type
                result["confidence"] = "high"
                result["detected_as"] = f"section: {sec_type}"
                result["suggested_id"] = suggest_sec_id(title)
                result["number"] = number
                return result
    
    # Tenta detectar como footnote
    fn_type = detect_fn_type(title)
    
    # Tenta detectar como seção
    sec_type, section_number = detect_sec_type_and_number(title)
    
    # Decide baseado no que foi detectado
    if fn_type and not sec_type:
        # Só detectou como footnote
        result["element_type"] = "fn"
        result["type_attribute"] = fn_type
        result["confidence"] = "high"
        result["detected_as"] = f"footnote: {fn_type}"
        result["number"] = extract_fn_number(title)
        result["suggested_id"] = suggest_fn_id(fn_type, result["number"])
        
    elif sec_type and not fn_type:
        # Só detectou como seção
        result["element_type"] = "sec"
        result["type_attribute"] = sec_type
        result["confidence"] = "high"
        result["detected_as"] = f"section: {sec_type}"
        result["number"] = section_number
        result["suggested_id"] = suggest_sec_id(title)
        
    elif fn_type and sec_type:
        # Detectou como ambos - precisa desambiguar
        # Usa contexto e heurísticas
        
        # Se está no back-matter, provavelmente é footnote
        if context == "back":
            result["element_type"] = "fn"
            result["type_attribute"] = fn_type
            result["confidence"] = "medium"
            result["detected_as"] = f"footnote (in back): {fn_type}"
            result["number"] = extract_fn_number(title)
            result["suggested_id"] = suggest_fn_id(fn_type, result["number"])
        
        # Se tem símbolo especial no início, provavelmente é footnote
        elif any(title.startswith(symbol) for symbol in SYMBOL_TO_FN_TYPE.keys()):
            result["element_type"] = "fn"
            result["type_attribute"] = fn_type
            result["confidence"] = "high"
            result["detected_as"] = f"footnote (symbol): {fn_type}"
            result["number"] = extract_fn_number(title)
            result["suggested_id"] = suggest_fn_id(fn_type, result["number"])
        
        # Se tem numeração de seção (2.1, etc), provavelmente é seção
        elif section_number and "." in section_number:
            result["element_type"] = "sec"
            result["type_attribute"] = sec_type
            result["confidence"] = "high"
            result["detected_as"] = f"section (numbered): {sec_type}"
            result["number"] = section_number
            result["suggested_id"] = suggest_sec_id(title)
        
        else:
            # Caso ambíguo - usa seção como padrão
            result["element_type"] = "sec"
            result["type_attribute"] = sec_type
            result["confidence"] = "low"
            result["detected_as"] = f"ambiguous (defaulting to section): {sec_type}"
            result["number"] = section_number
            result["suggested_id"] = suggest_sec_id(title)
            
    else:
        # Não detectou como nenhum dos dois
        result["confidence"] = "none"
        result["detected_as"] = "unidentified"
    
    return result


def extract_fn_number(text: str) -> Optional[str]:
    """
    Extrai o número ou símbolo de uma footnote.
    
    Args:
        text: Texto da footnote
    
    Returns:
        Número, letra ou símbolo extraído
    """
    if not text:
        return None
    
    for pattern in FN_NUMBER_PATTERNS:
        match = re.match(pattern, text)
        if match:
            return match.group(1)
    
    return None


def suggest_fn_id(fn_type: Optional[str], number: Optional[str] = None) -> str:
    """
    Sugere um ID para uma footnote baseado no tipo e número.
    
    Args:
        fn_type: Tipo da footnote
        number: Número ou símbolo da footnote
    
    Returns:
        ID sugerido para a footnote
    
    Exemplos:
        >>> suggest_fn_id("corresp", "1")
        'fn1'
        >>> suggest_fn_id("equal", "*")
        'fnast'
        >>> suggest_fn_id("financial-disclosure")
        'fn1'
    """
    if number:
        # Trata símbolos especiais
        symbol_map = {
            "*": "ast",
            "†": "dag",
            "‡": "ddag",
            "§": "sect",
            "¶": "para",
            "#": "hash",
            "**": "dast",
            "††": "ddag",
        }
        
        if number in symbol_map:
            return f"fn{symbol_map[number]}"
        else:
            # Remove caracteres não alfanuméricos
            clean_number = re.sub(r"[^\w]", "", number)
            return f"fn{clean_number}"
    else:
        return "fn1"


def batch_detect_element_types(titles: List[str], context: Optional[str] = None) -> List[Dict[str, Optional[str]]]:
    """
    Detecta tipos de múltiplos elementos em lote.
    
    Args:
        titles: Lista de títulos para análise
        context: Contexto opcional para todos os elementos
    
    Returns:
        Lista de resultados da detecção
    """
    results = []
    for title in titles:
        result = detect_element_type(title, context)
        result["original_title"] = title
        results.append(result)
    return results


# Exemplos de uso e testes
if __name__ == "__main__":
    print("=" * 80)
    print("SISTEMA DE DETECÇÃO DE TIPOS DE ELEMENTOS (SEC vs FN)")
    print("=" * 80)
    
    # Teste 1: Títulos claramente de seções
    print("\n1. TÍTULOS DE SEÇÕES:")
    print("-" * 40)
    
    section_titles = [
        "1. Introduction",
        "2. Materials and Methods",
        "Results",
        "Discussion",
        "Conclusões",
    ]
    
    for title in section_titles:
        result = detect_element_type(title)
        print(f"{title:<40} → {result['element_type']:<5} ({result['type_attribute']})")
    
    # Teste 2: Títulos claramente de footnotes
    print("\n2. TÍTULOS DE FOOTNOTES:")
    print("-" * 40)
    
    footnote_titles = [
        "*Corresponding author",
        "†These authors contributed equally",
        "Financial disclosure",
        "1. Author contributions",
        "Conflict of interest statement",
    ]
    
    for title in footnote_titles:
        result = detect_element_type(title)
        print(f"{title:<40} → {result['element_type']:<5} ({result['type_attribute']})")
    
    # Teste 3: Casos ambíguos
    print("\n3. CASOS AMBÍGUOS:")
    print("-" * 40)
    
    ambiguous_titles = [
        "Supplementary material",  # Pode ser sec ou fn
        "Abbreviations",  # Pode ser sec ou fn
        "Present address",  # Geralmente fn
        "Study group members",  # Geralmente fn
    ]
    
    for title in ambiguous_titles:
        result = detect_element_type(title)
        print(f"\n{title}:")
        print(f"  Element: {result['element_type']}")
        print(f"  Type: {result['type_attribute']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Detected as: {result['detected_as']}")
        print(f"  Suggested ID: {result['suggested_id']}")
    
    # Teste 4: Com contexto
    print("\n4. DETECÇÃO COM CONTEXTO:")
    print("-" * 40)
    
    test_with_context = [
        ("Abbreviations", "back"),
        ("Abbreviations", "body"),
        ("Financial support", "back"),
        ("Financial support", "body"),
    ]
    
    for title, ctx in test_with_context:
        result = detect_element_type(title, ctx)
        print(f"{title} (context: {ctx}):")
        print(f"  → {result['element_type']} / {result['type_attribute']} (conf: {result['confidence']})")
    
    # Teste 5: Detecção em lote
    print("\n5. DETECÇÃO EM LOTE:")
    print("-" * 40)
    
    mixed_titles = [
        "Introduction",
        "*Corresponding author: john.doe@example.com",
        "Materials and Methods",
        "†Equal contribution",
        "Results and Discussion",
        "Financial disclosure: This work was supported by grant XYZ",
        "Conclusions",
        "Data availability statement",
        "Conflict of interest: None declared",
        "Supplementary Material",
    ]
    
    batch_results = batch_detect_element_types(mixed_titles, context="back")
    
    print(f"{'Title':<50} {'Element':<8} {'Type':<25} {'Confidence':<10}")
    print("-" * 93)
    
    for result in batch_results:
        title_display = result['original_title'][:47] + "..." if len(result['original_title']) > 50 else result['original_title']
        print(f"{title_display:<50} {str(result['element_type']):<8} {str(result['type_attribute']):<25} {str(result['confidence']):<10}")
    
    # Teste 6: Extração de números de footnotes
    print("\n6. EXTRAÇÃO DE NÚMEROS DE FOOTNOTES:")
    print("-" * 40)
    
    footnotes_with_numbers = [
        "1. Corresponding author",
        "[2] Financial disclosure",
        "(a) Present address",
        "* Equal contribution",
        "† Deceased",
        "‡ On leave",
        "A. Supplementary data",
    ]
    
    for fn_text in footnotes_with_numbers:
        number = extract_fn_number(fn_text)
        fn_type = detect_fn_type(fn_text)
        suggested_id = suggest_fn_id(fn_type, number)
        print(f"{fn_text:<35} → number: {str(number):<5} → ID: {suggested_id}")
    
    # Teste 7: Casos especiais multilíngues
    print("\n7. CASOS MULTILÍNGUES:")
    print("-" * 40)
    
    multilingual_cases = [
        # Português
        "Conflito de interesses",
        "Contribuições dos autores",
        "Endereço atual",
        # Espanhol
        "Conflicto de interés",
        "Contribuciones de los autores",
        "Dirección actual",
        # Francês
        "Conflit d'intérêt",
        "Contributions des auteurs",
        "Adresse actuelle",
        # Alemão
        "Interessenkonflikt",
        "Autorenbeiträge",
        "Aktuelle Adresse",
    ]
    
    for title in multilingual_cases:
        result = detect_element_type(title)
        print(f"{title:<40} → {result['element_type']}/{result['type_attribute']}")
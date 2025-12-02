import re
from typing import Dict, Optional, Tuple, List
import unicodedata
from scielo_migration.scielo_classic_website.spsxml.detector_config_xref import (
    REF_TYPE_TO_ELEMENT, ID_PATTERNS, TEXT_PATTERNS, REF_TYPE_TO_ID_PREFIX
)
from scielo_migration.scielo_classic_website.spsxml.detector_config_sec import SEC_TYPE_PATTERNS, COMBINED_PATTERNS


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


def detect_from_text(text: str, context: Optional[str] = None) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
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


def get_id_prefix_and_number(text: str, ref_type: Optional[str] = None) -> str:
    """
    Gera um ID apropriado a partir do texto da referência.
    
    Args:
        text: Texto da referência
        ref_type: Tipo já identificado (opcional)
        
    Returns:
        ID gerado no formato padrão
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
        'ref_type': None,
        'element_name': None,
        'prefix': None,
        'number': None,
        'rid': None,
        'source': None,
        'consistent': None
    }
    
    prefix = None
    number = None
    ref_type_text = None
    element_name_text = None

    # Análise do texto
    if text:
        ref_type_text, element_name_text, prefix, number = detect_from_text(text)
        if ref_type_text:
            result['ref_type'] = ref_type_text
            result['element_name'] = element_name_text
            result['prefix'] = prefix
            result['number'] = number
            result['source'] = 'text'
    
    # Análise do ID
    if rid:
        ref_type_id, element_name_id = detect_from_id(rid)
        if ref_type_id:
            if result['ref_type']:
                # Tem ambos, verifica consistência
                result['consistent'] = (
                    ref_type_text == ref_type_id and
                    element_name_text == element_name_id
                )
                # Prefere o RID fornecido se consistente
                if result['consistent']:
                    result['rid'] = rid
                    result['source'] = 'both'
            else:
                # Só tem ID
                result['ref_type'] = ref_type_id
                result['element_name'] = element_name_id
                result['rid'] = rid
                result['source'] = 'id'
    
    return result


def normalize_id(id_string: str) -> str:
    """
    Normaliza um ID para ser válido em XML.
    """
    # Remove acentos
    normalized = unicodedata.normalize('NFKD', id_string)
    normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])
    
    # Remove caracteres inválidos
    normalized = re.sub(r'[^a-zA-Z0-9_\-\.]', '', normalized)
    
    # Garante que comece com letra ou underscore
    if normalized and not re.match(r'^[a-zA-Z_]', normalized):
        normalized = '_' + normalized
    
    return normalized or 'id1'


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
        result = analyze_xref(
            text=xref.get('text'),
            rid=xref.get('rid')
        )
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
            if part.strip() and part.strip() not in ['and', '&', 'e', 'y', 'et', 'und', 'en', 'com', 'avec', 'mit', 'met']:
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


def detect_sec_type_and_number(section_text: str) -> Tuple[Optional[str], Optional[str]]:
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
            title_without_number = text[match.end():].strip()
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
        number = number.replace('.', '_')
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
        
        results.append({
            'title': title,
            'sec_type': sec_type,
            'number': number,
            'suggested_id': suggested_id
        })
    
    return results


# Exemplos de uso e testes
if __name__ == "__main__":
    print("=" * 80)
    print("SISTEMA DE ANÁLISE BIDIRECIONAL DE XREFS")
    print("=" * 80)
    
    # Teste 1: Análise a partir de texto
    print("\n1. ANÁLISE A PARTIR DE TEXTO:")
    print("-" * 40)
    
    test_texts = [
        # Múltiplos idiomas
        "Figure 1", "Figura 2", "Abbildung 3", "Figuur 4",
        "Table 1", "Tableau 2", "Tabelle 3", "Tabel 4",
        "Equation 1", "Équation 2", "Gleichung 3",
        "Section 2.1", "Sección 3", "Chapitre 4",
        # Referências bibliográficas
        "Silva et al., 2024",
        "García y col., 2023",
        "Schmidt u.a., 2022",
        "Van Der Merwe en ander, 2021",
    ]
    
    for text in test_texts:
        ref_type, element_name, prefix, number = detect_from_text(text)
        rid = f"{prefix}{number}" if prefix and number else None
        print(f"{text:<30} → ref_type: {ref_type:<15} element: {element_name:<20} rid: {rid}")
    
    # Teste 2: Análise a partir de IDs
    print("\n2. ANÁLISE A PARTIR DE IDs:")
    print("-" * 40)
    
    test_ids = [
        "f1", "f2a", "t3", "B42", "sec2_1", "app1",
        "e5", "TFN1", "suppl3", "S2", "fnast", "fndag"
    ]
    
    for rid in test_ids:
        ref_type, element_name = detect_from_id(rid)
        print(f"{rid:<15} → ref_type: {ref_type:<20} element: {element_name}")
    
    # Teste 3: Análise bidirecional completa
    print("\n3. ANÁLISE BIDIRECIONAL COMPLETA:")
    print("-" * 40)
    
    test_cases = [
        {"text": "Figure 1", "rid": "f1"},
        {"text": "Tabla 2", "rid": "t2"},
        {"text": "Section 3.1", "rid": "sec3_1"},
        {"text": "Fig. 4", "rid": "wrong5"},  # Inconsistente
        {"text": "Equation 2"},  # Só texto
        {"rid": "B15"},  # Só ID
    ]
    
    for test in test_cases:
        result = analyze_xref(**test)
        print(f"\nInput: {test}")
        print(f"Result: ref_type={result['ref_type']}, element={result['element_name']}, "
              f"rid={result['rid']}, source={result['source']}, consistent={result['consistent']}")
    
    # Teste 4: Análise em lote
    print("\n4. ANÁLISE EM LOTE:")
    print("-" * 40)
    
    batch = [
        {'text': 'Figure 1'},
        {'text': 'Tableau 2', 'rid': 't2'},
        {'rid': 'B3'},
        {'text': 'Gleichung 4'},
        {'text': 'Material Suplementar S1'},
    ]
    
    results = batch_analyze_xrefs(batch)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {batch[i-1]}")
        print(f"   → {result['ref_type']}/{result['element_name']}/{result['rid']}")
    
    # Teste 5: Detecção de sec-type
    print("\n" + "=" * 80)
    print("5. DETECÇÃO DE SEC-TYPE:")
    print("-" * 40)
    
    section_titles = [
        # Inglês
        "Introduction",
        "Materials and Methods",
        "Results",
        "Discussion",
        "Results and Discussion",
        "Conclusions",
        "Data Availability",
        "Participants",
        "Patients and Methods",
        # Português
        "Introdução",
        "Material e Métodos",
        "Metodologia",
        "Resultados e Discussão",
        "Conclusões",
        "Disponibilidade de Dados",
        "Pacientes e Métodos",
        # Espanhol
        "Introducción",
        "Materiales y Métodos",
        "Resultados",
        "Discusión",
        "Resultados y Discusión",
        "Conclusiones",
        # Francês
        "Introduction",
        "Matériaux et Méthodes",
        "Résultats",
        "Discussion",
        "Résultats et Discussion",
        # Alemão
        "Einleitung",
        "Material und Methoden",
        "Ergebnisse",
        "Diskussion",
        "Ergebnisse und Diskussion",
        "Schlussfolgerungen",
        # Africâner
        "Inleiding",
        "Materiaal en Metodes",
        "Resultate",
        "Bespreking",
        "Resultate en Bespreking",
        # Casos combinados especiais
        "Conclusions and Future Work",
        "Cases and Results",
        "Conclusions and Recommendations",
    ]
    
    print(f"{'Título da Seção':<40} {'sec-type detectado':<30}")
    print("-" * 70)
    
    for title in section_titles:
        sec_type = detect_sec_type(title)
        print(f"{title:<40} {str(sec_type):<30}")
    
    # Teste 6: Detecção de sec-type com números
    print("\n6. DETECÇÃO DE SEC-TYPE E NÚMEROS:")
    print("-" * 40)
    
    numbered_sections = [
        "1. Introduction",
        "2. Materials and Methods",
        "2.1 Study Population",
        "2.2 Experimental Procedures",
        "3. Results",
        "3.1. Clinical Cases",
        "4. Discussion",
        "4.1 Results and Discussion",
        "5. Conclusions",
        "A. Supplementary Material",
        "I. Introdução",
        "II. Material e Métodos",
    ]
    
    print(f"{'Título':<40} {'sec-type':<25} {'número':<10} {'ID':<10}")
    print("-" * 85)
    
    for section in numbered_sections:
        sec_type, number = detect_sec_type_and_number(section)
        suggested_id = suggest_sec_id(section)
        print(f"{section:<40} {str(sec_type):<25} {str(number):<10} {suggested_id:<10}")
    
    # Teste 7: Detecção em lote
    print("\n7. DETECÇÃO EM LOTE DE SEÇÕES:")
    print("-" * 40)
    
    article_sections = [
        "1. Introduction",
        "2. Study Design and Participants",
        "3. Materials and Methods",
        "4. Results and Discussion",
        "5. Cases and Results",
        "6. Conclusions and Future Work",
        "7. Data Availability Statement",
        "Appendix A: Supplementary Material"
    ]
    
    batch_results = batch_detect_sec_types(article_sections)
    
    print(f"{'Título':<45} {'sec-type':<30} {'ID':<10}")
    print("-" * 85)
    
    for result in batch_results:
        print(f"{result['title']:<45} {str(result['sec_type']):<30} {result['suggested_id']:<10}")
    
    # Teste 8: Casos especiais de múltiplos tipos
    print("\n8. CASOS ESPECIAIS - MÚLTIPLOS TIPOS:")
    print("-" * 40)
    
    special_cases = [
        "Materials and Methods",
        "Material e Métodos",
        "Matériaux et Méthodes",
        "Results and Discussion",
        "Resultados e Discussão",
        "Patients and Methods",
        "Cases and Results",
        "Introduction and Objectives",
        "Methods and Procedures",
        "Conclusions and Recommendations",
        "Discussion and Conclusions",
    ]
    
    print(f"{'Título':<45} {'sec-type (com | para múltiplos)':<35}")
    print("-" * 80)
    
    for title in special_cases:
        sec_type = detect_sec_type(title)
        print(f"{title:<45} {str(sec_type):<35}")
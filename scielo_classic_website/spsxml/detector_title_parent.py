"""
Identificador semântico de elemento pai para <title> em JATS/SPS.
"""

import re
from typing import Optional


# Dicionário global de padrões -> elemento pai
PATTERNS = {
    # Abstract e traduções
    r'^(abstract|resumo|resumen|résumé|zusammenfassung|摘要|要約|резюме)': 'abstract',
    r'^(summary|sumário|sommario|sommaire|síntesis)': 'abstract',
    
    # Trans-abstract (abstracts traduzidos com indicação de idioma)
    r'^(abstract|resumo|resumen|résumé).*(english|inglês|español|português|français|castellano|espanhol)': 'trans-abstract',
    r'^(traducción|translation|tradução|traduction)': 'trans-abstract',
    
    # Sections
    r'^(introduction|introdução|introducción|einleitung|介绍|はじめに)': 'sec',
    r'^(methods?|métodos?|metodolog|materials?\s+and\s+methods?|materiales?\s+y\s+métodos?)': 'sec',
    r'^(results?|resultados?|hallazgos?)': 'sec',
    r'^(discussion|discussão|discusión|diskussion|debate)': 'sec',
    r'^(conclusion|conclusão|conclusión|conclusiones?|consideraciones?\s+finales?)': 'sec',
    
    # References
    r'^(references?|referências|referencias|bibliograf|literature\s+cited|works\s+cited|obras?\s+citadas?|lecturas?\s+recomendadas?)': 'ref-list',
    r'^(citation|citações|citas|citación)': 'ref-list',
        
    # Acknowledgments
    r'^(acknowledg|agradec|reconoc|remerci|dank)': 'ack',
    
    # Appendix/Supplement
    r'^(append|apêndice|apéndice|anexo|anejo|supp?lement)': 'app',
    r'^(supplementary|material\s+suplementar|material\s+complementario|información\s+adicional)': 'supplementary-material',
    
    # Notes and footnotes
    r'^(notes?|notas?|observa|anmerkung|anotaciones?)': 'fn-group',
    r'^(footnote|nota\s+de\s+rodapé|nota\s+al\s+pie|pie\s+de\s+página|nota\s+a\s+pie)': 'fn-group',
    
    # Author information
    r'^(author|autor|autores?|auteur|verfasser).*?(note|nota|info|biograph|información)': 'author-notes',
    r'^(biograph|biograf|vita|curriculum|semblanza|reseña\s+biográfica)': 'bio',
    
    # Keywords
    r'^(key[\s-]?words?|palavras?[\s-]chave|palabras?[\s-]clave|descriptors?|descriptores?|termos?[\s-]chave|términos?[\s-]clave)': 'kwd-group',
    
    # Glossary
    r'^(glossary|glossário|glosario|lexique|wörterbuch|vocabulario|léxico)': 'glossary',
    
    # Questions (Q&A sections)
    # r'^(question|pergunta|pregunta|frage|questão|cuestión|interrogante)': 'question',
    # r'^(answer|resposta|respuesta|antwort|contestación)': 'answer',
    
    # Lists and definitions
    r'^(definition|definição|definición|définition|concepto)': 'def-list',
    
    # Captions and legends
    r'^(figure|figura|abbildung|fig\.|ilustra|gráfico)': 'caption',
    r'^(table|tabela|tabla|tableau|cuadro|quadro)': 'caption',
    r'^(legend|legenda|leyenda|légende|explicación)': 'legend',
}


def identify_parent_by_title(title_content: str) -> Optional[str]:
    """
    Identifica o elemento pai baseado no conteúdo do título.
    
    Args:
        title_content: Texto do elemento <title>
        
    Returns:
        Nome do elemento pai ou None se não identificado
    """
    
    # Normaliza o texto para comparação
    text = title_content.strip().lower()
    
    # Testa cada padrão
    for pattern, parent in PATTERNS.items():
        if re.search(pattern, text):
            return parent
    
    # Se não encontrou padrão específico, pode ser uma seção genérica
    # se tiver numeração como "1.", "2.1", etc.
    if re.match(r'^\d+\.?\d*\.?\s+\w+', text):
        return 'sec'
    
    return None


def process_titles(titles: list) -> dict:
    """
    Processa uma lista de títulos e retorna mapeamento.
    
    Args:
        titles: Lista de strings com conteúdo dos títulos
        
    Returns:
        Dicionário {título: elemento_pai}
    """
    results = {}
    for title in titles:
        parent = identify_parent_by_title(title)
        if parent:
            results[title] = parent
    return results


# Exemplo de uso
if __name__ == "__main__":
    test_titles = [
        "Abstract",
        "Resumo",
        "Introduction",
        "Materials and Methods",
        "References",
        "Acknowledgments",
        "Figure 1. Sample diagram",
        "Palavras-chave",
        "1. Background",
        "Appendix A"
    ]
    
    for title in test_titles:
        parent = identify_parent_by_title(title)
        print(f"'{title}' -> {parent if parent else 'não identificado'}")
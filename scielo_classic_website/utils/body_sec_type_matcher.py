import logging
import difflib
import re
import unicodedata


SECTION_TYPES = [
    'cases',
    'conclusions',
    'data-availability',
    'discussion',
    'intro',
    'materials',
    'methods',
    'results',
    'subjects',
    'supplementary-material',
    'transcript'
]

SECTION_TYPES_TO_IGNORE = [
    'abstract',
    'resumen',
    'references',
    'agradecimientos',
    'acknownledge',
]

STD = {
    
    "literatura citada":  "references",
}


def get_best_matches(section_title, n=None, cutoff=None):
    # Encontra as 3 melhores correspondências com pelo menos 60% de similaridade
    n = n or 1
    cutoff = cutoff or 0.1
    return difflib.get_close_matches(
        section_title, 
        SECTION_TYPES+SECTION_TYPES_TO_IGNORE, 
        n,           # número máximo de resultados
        cutoff     # similaridade mínima (0 a 1)
    )

def ignore(section_title):
    if len(section_title.split()) > 3:
        return


def get_sectype(section_title, n=None, cutoff=None):
    section_title_parts = section_title.split(" ")
    total_words = len(section_title_parts)
    if total_words > 3:
        return

    section_title = STD.get(section_title) or section_title
    words = [section_title]
    if total_words == 1:
        cutoff = 0.4
    elif total_words == 3:
        cutoff = 0.6
        words = [section_title_parts[0], section_title_parts[-1]]
    else:
        cutoff = 0.4

    try:
        sectypes = []
        for word in words:
            response = get_best_matches(word, 1, cutoff)
            if not response or response[0] in SECTION_TYPES_TO_IGNORE:
                continue            
            sectypes.extend(response)
        return "|".join(sectypes)
    except (TypeError, ValueError):
        return None

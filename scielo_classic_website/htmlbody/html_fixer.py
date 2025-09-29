import logging
from datetime import datetime
from difflib import SequenceMatcher


from lxml.html import fromstring, tostring


# Constantes globais
HTML_NAMESPACES = ' xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns:st1="urn:schemas-microsoft-com:office:smarttags"'

DEFAULT_STYLE_MAPPINGS = {
    "b": "bold",
    "i": "italic", 
    "u": "underline",
    "sup": "sup",
    "sub": "sub"
}

DEFAULT_TAGS_TO_FIX = ("p", )


def get_html_fixed_or_original(original):
    fixed_html = get_fixed_html(original)

    tagless_html = remove_tags(fixed_html)
    tagless_text = get_fixed_text(original)

    std_converted = tagless_html.split()
    std_original = tagless_text.split()

    score = SequenceMatcher(None, std_original, std_converted).ratio()
    if score == 1:
        return fixed_html

    # now = datetime.now().isoformat()

    # rows = [
    #     original,
    #     tagless_html,
    #     tagless_text,
    # ]
    
    # with open(f"_diff_{now}.txt", "w") as fp:
    #     fp.write("\n--------\n".join(rows))

    if score > 0.7:
        return fixed_html

    return original


def load_html(content):
    return fromstring(wrap_html(content))


def get_fixed_html(content, style_mappings=None, tags_to_fix=None, remove_namespaces=True):
    """
    Função principal que retorna o conteúdo HTML corrigido e convertido para XML.
    
    Args:
        content: Conteúdo HTML a ser processado
        style_mappings: Mapeamento customizado de tags para estilos
        tags_to_fix: Tags que devem ter balanceamento corrigido
        remove_namespaces: Se deve remover tags com namespaces
        
    Returns:
        Conteúdo processado e convertido para XML
    """
    style_mappings = style_mappings or DEFAULT_STYLE_MAPPINGS
    tags_to_fix = tags_to_fix or DEFAULT_TAGS_TO_FIX
    
    fixed_content = fix(content, style_mappings, tags_to_fix)
    wrapped = wrap_html(fixed_content)
    tree = fromstring(wrapped)
    return html2xml(tree)


def get_fixed_text(content):
    """
    Retorna o conteúdo HTML sem tags e convertido para XML.
    
    Args:
        content: Conteúdo HTML a ser processado
        
    Returns:
        Conteúdo processado sem tags e convertido para XML
    """
    content_no_tags = remove_tags(content)
    wrapped = wrap_html(content_no_tags)
    tree = fromstring(wrapped)
    return remove_tags(html2xml(tree))


def fix(content, style_mappings=None, tags_to_fix=None):
    """
    Aplica todas as correções ao conteúdo HTML.
    
    Args:
        content: Conteúdo HTML a ser processado
        style_mappings: Mapeamento customizado de tags para estilos
        tags_to_fix: Tags que devem ter balanceamento corrigido
        remove_namespaces: Se deve remover tags com namespaces
        
    Returns:
        Conteúdo processado
    """
    style_mappings = style_mappings or DEFAULT_STYLE_MAPPINGS
    tags_to_fix = tags_to_fix or DEFAULT_TAGS_TO_FIX
    
    # Pipeline de processamento
    content = avoid_mismatched_styles(content, style_mappings)
    content = avoid_mismatched_tags(content, tags_to_fix)
    content = remove_namespaces_from_content(content)
    return content


def avoid_mismatched_styles(content, style_mappings=None):
    """
    Converte tags de estilo antigas para spans modernos.
    
    Args:
        content: Conteúdo HTML
        style_mappings: Mapeamento de tags para estilos
        
    Returns:
        Conteúdo com tags de estilo convertidas
    """
    style_mappings = style_mappings or DEFAULT_STYLE_MAPPINGS
    
    for tag, style in style_mappings.items():
        # Tags minúsculas
        content = content.replace(f"<{tag}>", f'<span name="style_{style}">')
        content = content.replace(f"</{tag}>", '</span>')
        
        # Tags maiúsculas
        tag_upper = tag.upper()
        content = content.replace(f"<{tag_upper}>", f'<span name="style_{style}">')
        content = content.replace(f"</{tag_upper}>", '</span>')
    
    return content


def avoid_mismatched_tags(content, tags_to_fix=None):
    """
    Corrige tags mal formadas ou não balanceadas.
    
    Args:
        content: Conteúdo HTML
        tags_to_fix: Tags que devem ter balanceamento corrigido
        
    Returns:
        Conteúdo com tags corrigidas
    """
    tags_to_fix = tags_to_fix or DEFAULT_TAGS_TO_FIX
    
    # Normaliza tags P para minúsculas (caso especial sempre aplicado)
    content = content.replace("<P>", "<p>")
    content = content.replace("</P>", "</p>")
    
    for tag_name in tags_to_fix:
        tag_open = f"<{tag_name}>"
        tag_close = f"</{tag_name}>"
        
        # Processa linha por linha para tags não balanceadas
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            if tag_open not in line and tag_close not in line:
                processed_lines.append(line)
                continue
            
            if tag_open in line and tag_close in line:
                processed_lines.append(line)
                continue
            
            if tag_open in line:
                line = line.replace(tag_open, f'<{tag_name} type="open"/>')
            
            if tag_close in line:
                line = line.replace(tag_close, f'<{tag_name} type="close"/>')
            
            processed_lines.append(line)
        
        content = '\n'.join(processed_lines)
    
    return content


def remove_namespaces_from_content(content):
    """
    Remove tags com namespaces do conteúdo.
    
    Args:
        content: Conteúdo HTML
        
    Returns:
        Conteúdo sem tags com namespaces
    """
    return "".join(get_no_namespaces(content))


def get_no_namespaces(content):
    """
    Gerador que retorna conteúdo sem tags com namespaces.
    
    Args:
        content: Conteúdo HTML
        
    Yields:
        Partes do conteúdo sem namespaces
    """
    for item in break_content(content):
        if (item or "").strip():
            if item and item[0] == "<" and item[-1] == ">":
                if tag_has_namespace(item):
                    continue
        yield item


def remove_tags(content):
    """
    Remove todas as tags HTML do conteúdo.
    
    Args:
        content: Conteúdo HTML
        
    Returns:
        Conteúdo sem tags
    """
    return "".join(get_tagless_items(content))


def get_tagless_items(content):
    """
    Gerador que retorna apenas o conteúdo sem tags HTML.
    
    Args:
        content: Conteúdo HTML
        
    Yields:
        Partes do conteúdo sem tags
    """
    for item in break_content(content):
        if (item or "").strip():
            if item and item[0] == "<" and item[-1] == ">":
                continue
        yield item


def wrap_html(content):
    """
    Envolve o conteúdo com tags HTML e namespaces.
    
    Args:
        content: Conteúdo a ser envolvido
        
    Returns:
        HTML completo com namespaces
    """
    content = content.strip()
    if "<HTML" in content:
        content = content.replace("<HTML", "<html").replace("</HTML>", "</html>")

    if "<html" not in content:
        return f"<html{HTML_NAMESPACES}><body>{content}</body></html>"

    if HTML_NAMESPACES in content:
        return content

    return content.replace("<html", f"<html{HTML_NAMESPACES}")


def break_content(content):
    """
    Quebra o conteúdo em partes separando tags de texto.
    
    Args:
        content: Conteúdo a ser quebrado
        
    Returns:
        Tupla com as partes do conteúdo
    """
    x = " ".join(content.split())
    x = x.replace("<", "BREAKTAGMARKS<")
    x = x.replace(">", ">BREAKTAGMARKS")
    return x.split("BREAKTAGMARKS")


def tag_has_namespace(tag):
    """
    Verifica se uma tag contém namespace.
    
    Args:
        tag: Tag a ser verificada
        
    Returns:
        True se a tag contém namespace
    """
    if ":" not in tag:
        return False
    for part in tag.split():
        if ":" in part.split("=")[0]:
            return True
    return False


def html2xml(tree):
    """
    Converte a árvore HTML para string XML.
    
    Args:
        tree: Árvore HTML
        
    Returns:
        Conteúdo XML do body
    """
    body = tree.find(".//body")
    try:
        content = tostring(body, method="xml", encoding="utf-8").decode("utf-8")
        content = content[content.find(">")+1:]
        content = content[:content.rfind("</body>")]
    except Exception as e:
        logging.exception(e)
        raise
    return content


# Exemplos de uso:
if __name__ == "__main__":
    # Exemplo 1: Corrigir HTML com configurações padrão
    html_content = "<P>Texto com <b>negrito</b> e <i>itálico</i></P>"
    fixed = get_fixed_html(html_content)
    print("HTML corrigido:", fixed)
    
    # Exemplo 2: Obter apenas texto sem tags
    text_only = get_fixed_text(html_content)
    print("Texto sem tags:", text_only)
    
    # Exemplo 3: Usar mapeamentos customizados
    custom_mappings = {
        "b": "strong",
        "i": "emphasis",
        "u": "underline",
        "strike": "strikethrough"
    }
    fixed_custom = get_fixed_html(html_content, style_mappings=custom_mappings)
    print("HTML com mapeamentos customizados:", fixed_custom)
    
    # Exemplo 4: Processar sem remover namespaces
    html_with_ns = '<p>Texto com <o:p>namespace</o:p></p>'
    fixed_with_ns = get_fixed_html(html_with_ns, remove_namespaces=False)
    print("HTML mantendo namespaces:", fixed_with_ns)
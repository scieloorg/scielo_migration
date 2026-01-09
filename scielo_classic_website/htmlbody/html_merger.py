"""
Módulo para mesclar conteúdo de arquivos HTML locais usando lxml.
Processa cada arquivo apenas uma vez, criando <xref> com texto original para referências repetidas.
"""

import os
from lxml import etree, html
from typing import Dict, Set, Optional, Callable, Tuple
from urllib.parse import urlparse


def normalize_path(file_path: str, base_path: str = None) -> str:
    """Normaliza o caminho combinando com base_path se fornecido."""
    if not file_path:
        return file_path
    
    # Se o caminho é absoluto, retorna como está
    if os.path.isabs(file_path):
        return file_path
    
    # Se temos um base_path, junta os caminhos
    if base_path:
        return os.path.join(base_path, file_path)
    
    # Caso contrário, retorna o caminho como está
    return file_path


def default_file_reader(file_path: str, encoding: str = 'utf-8', base_path: str = None) -> str:
    """Lê arquivo do sistema de arquivos."""
    path = normalize_path(file_path, base_path)
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


class HTMLMerger:
    """Mescla conteúdo de HTMLs referenciados, processando cada arquivo uma única vez."""
    
    def __init__(
        self, 
        journal_acron_folder: str = None, 
        encoding: str = 'utf-8',
        content_reader: Callable = None
    ):
        self.journal_acron_folder = journal_acron_folder
        self.encoding = encoding
        self.content_reader = content_reader or default_file_reader
        self.embedded_files: Set[str] = set()  # arquivos já processados
        self.processing_stack: Set[str] = set()  # evita recursão circular
        # Parser HTML do lxml
        self.parser = html.HTMLParser(encoding=encoding)
    
    def is_link_to_local_html_file(self, href: str) -> bool:
        """Verifica se o link deve ser processado."""
        if not href:
            return False

        # Ignora links externos e especiais
        excluded = ('mailto:', 'javascript:', '#')
        if href.startswith(excluded):
            return False

        if self.journal_acron_folder and self.journal_acron_folder not in href:
            # journal_acron_folder == path que contém /journal_acron/
            return False

        # Ignora links externos e especiais
        excluded = ('http://', 'https://')
        if href.startswith(excluded):
            # tornar url remota em local
            parsed = urlparse(href)
            href = parsed.path
        
        # Processa apenas HTML
        file_path = href.split('#')[0]
        return file_path and file_path.endswith(('.html', '.htm'))
    
    def parse_href(self, href: str) -> Tuple[str, str]:
        """Extrai arquivo e âncora do href."""
        excluded = ('http://', 'https://')
        if href.startswith(excluded):
            # tornar url remota em local
            parsed = urlparse(href)
            href = parsed.path
        if '#' in href:
            file_path, anchor = href.split('#', 1)
        else:
            file_path, anchor = href, ''

        return file_path, anchor
    
    def read_content(self, file_path: str, base_path: str = None) -> Optional[str]:
        """Lê conteúdo usando o reader configurado, passando base_path."""
        try:
            # Passa file_path, encoding e base_path para o reader
            return self.content_reader(file_path, self.encoding, self.journal_acron_folder or base_path)
        except FileNotFoundError:
            print(f"Aviso: arquivo não encontrado - {file_path}")
            return None
        except Exception as e:
            print(f"Erro ao ler {file_path}: {e}")
            return None

    def create_embed_element(self, file_path: str, anchor: str, 
                           label: str, embed: etree.Element) -> etree.Element:
        """Cria elemento html-to-embed com conteúdo."""
        embed.tag = 'html-to-embed'
        embed.set('path', file_path)
        if anchor:
            embed.set('anchor', anchor)
        embed.set('label', label)
        return embed
    
    def create_xref_element(self, file_path: str, anchor: str, 
                          link_element: etree.Element) -> etree.Element:
        """Cria elemento xref mantendo o conteúdo original do link."""
        xref = etree.Element('xref')
        xref.set('asset_type', 'html')
        xref.set('path', file_path)
        if anchor:
            xref.set('anchor', anchor)
        
        # Copia texto inicial do link
        xref.text = link_element.text
        
        # Copia todos os filhos do link
        for child in link_element:
            xref.append(child)
        
        # Preserva o tail (texto após o elemento)
        xref.tail = link_element.tail
        
        return xref
    
    def get_file_key(self, file_path: str, base_path: str) -> str:
        """Gera chave única para identificar arquivo processado."""
        return file_path
    
    def is_already_processed(self, file_key: str) -> bool:
        """Verifica se o arquivo já foi processado."""
        return file_key in self.embedded_files
    
    def is_being_processed(self, file_key: str) -> bool:
        """Verifica se está em processamento (recursão circular)."""
        return file_key in self.processing_stack
    
    def process_html_content(self, file_path: str, base_path: str) -> Optional[str]:
        """Processa o conteúdo de um arquivo se ainda não foi processado."""
        file_key = self.get_file_key(file_path, base_path)
        
        # Verifica se já foi processado - retorna None pois não precisa do conteúdo
        if self.is_already_processed(file_key):
            return None
        
        # Verifica recursão circular
        if self.is_being_processed(file_key):
            print(f"Aviso: referência circular detectada - {file_path}")
            return None
        
        # Marca como em processamento
        self.processing_stack.add(file_key)
        
        try:
            # Lê conteúdo - passa base_path para o reader
            content = self.read_content(file_path, base_path)
            if content is None:
                return None
            
            # Processa recursivamente
            # Para recursão, o novo base é o diretório do arquivo atual
            processed = self.process_html_internal(content, base_path)
            
            # Marca como processado
            self.embedded_files.add(file_key)
            return processed
            
        finally:
            # Remove da pilha de processamento
            self.processing_stack.discard(file_key)
    
    def process_single_link(self, link_element: etree.Element, base_path: str) -> Optional[etree.Element]:
        """Processa um único link, retornando elemento embed ou xref conforme necessário."""
        href = link_element.get('href', '')
        
        if not self.is_link_to_local_html_file(href):
            return None
        
        file_path, anchor = self.parse_href(href)
        file_key = self.get_file_key(file_path, base_path)
        
        # Verifica se já foi processado ANTES de tentar processar
        html_body_node = None
        if not self.is_already_processed(file_key):
            html_body_node = self.process_html_content(file_path, base_path)
        
        if html_body_node is not None:
            # Sucesso: cria html-to-embed
            label = ''.join(link_element.itertext()).strip()
            return self.create_embed_element(file_path, anchor, label, html_body_node)
        else:
            # Erro ao processar ou circular ou já processado - cria xref
            return self.create_xref_element(file_path, anchor, link_element)
    
    def process_html_internal(self, html_content: str, base_path: str = None) -> etree.Element:
        """Processa HTML internamente (para recursão)."""
        try:
            # Parse do HTML
            doc = html.fromstring(html_content, parser=self.parser)
            
            # Encontra todos os links
            links = doc.xpath('//a[@href]')
            
            # Processa cada link
            for link in links:
                new_element = self.process_single_link(link, base_path)
                if new_element is not None:
                    # Substitui o link pelo novo elemento
                    parent = link.getparent()
                    if parent is not None:
                        parent.replace(link, new_element)
            
            # Retorna HTML serializado
            return doc.find(".//body")
            
        except Exception as e:
            print(f"Erro ao processar HTML: {e}")
            return html_content
    
    def process_html(self, html_content: str, base_path: str = None) -> str:
        """Processa HTML incorporando referências locais (API pública)."""
        # Limpa estado para novo processamento
        self.embedded_files.clear()
        self.processing_stack.clear()
        return self.process_html_internal(html_content, base_path)


def merge_html(
    input_html: str,
    journal_acron_folder: str = None,
    encoding: str = 'utf-8',
    content_reader: Callable = None
) -> etree.Element:
    """
    Mescla referências HTML, processando cada arquivo uma única vez.
    
    Args:
        input_html: HTML string ou caminho do arquivo
        journal_acron_folder: Diretório base para resolver paths
        output_file: Arquivo de saída (opcional)
        encoding: Encoding dos arquivos
        content_reader: Função para ler conteúdo
                       Assinatura: (file_path: str, encoding: str, journal_acron_folder: str) -> str
    
    Returns:
        HTML processado com elementos html-to-embed e xref
    
    Examples:
        >>> # Reader customizado que recebe journal_acron_folder
        >>> def my_reader(path, encoding, journal_acron_folder):
        ...     full_path = normalize_path(path, journal_acron_folder)
        ...     return get_content(full_path)
        >>> result = merge_html(html, content_reader=my_reader)
    """
    merger = HTMLMerger(journal_acron_folder, encoding, content_reader)
    
    # Processa string
    return merger.process_html(input_html)


# ===== EXEMPLOS DE USO =====

if __name__ == "__main__":
    # Exemplo com links repetidos
    html_example = '''
    <html>
    <body>
        <h1>Documento com Referências</h1>
        
        <p>Primeira: <a href="figura.html#fig1">Figura 1</a></p>
        <p>Segunda: <a href="figura.html">Ver figura completa</a></p>
        <p>Terceira: <a href="figura.html#fig1">Figura 1 novamente</a></p>
        
        <p>Subdiretório: <a href="imgs/foto.html">Foto</a></p>
        <p>Mesma foto: <a href="imgs/foto.html">Ver foto</a></p>
        
        <p>Link externo: <a href="https://example.com">Site externo</a></p>
    </body>
    </html>
    '''
    
    print("HTML Original:")
    print(html_example)
    print("\n" + "="*50 + "\n")
    
    # Mock reader que recebe journal_acron_folder
    def mock_reader(path: str, encoding: str, journal_acron_folder: str) -> str:
        # Usa normalize_path para resolver o caminho
        full_path = normalize_path(path, journal_acron_folder)
        print(f"Reader chamado: path='{path}', journal_acron_folder='{journal_acron_folder}' -> '{full_path}'")
        
        files = {
            "figura.html": "<div>Conteúdo da figura</div>",
            "imgs/foto.html": "<img src='foto.jpg' alt='Foto'/>",
            os.path.join("imgs", "foto.html"): "<img src='foto.jpg' alt='Foto'/>"
        }
        
        # Tenta várias combinações
        for key in [path, full_path, os.path.normpath(full_path)]:
            if key in files:
                return files[key]
                
        raise FileNotFoundError(f"Mock: {path} não encontrado")
    
    merger = HTMLMerger(content_reader=mock_reader)
    result_doc = merger.process_html(html_example)
    
    # Verifica html-to-embed
    embeds = result_doc.xpath('//html-to-embed')
    print(f"Total de html-to-embed: {len(embeds)}")
    for embed in embeds:
        print(f"  - path: {embed.get('path')}, label: {embed.get('label')}")
    
    # Verifica xref
    xrefs = result_doc.xpath('//xref')
    print(f"Total de xref: {len(xrefs)}")
    for xref in xrefs:
        print(f"  - path: {xref.get('path')}, texto: {''.join(xref.itertext()).strip()}")
    
    # Verifica links externos preservados
    external_links = result_doc.xpath('//a[starts-with(@href, "http")]')
    print(f"Links externos preservados: {len(external_links)}")
    for link in external_links:
        print(f"  - href: {link.get('href')}, texto: {''.join(link.itertext()).strip()}")
"""
Módulo para navegação recursiva de HTMLs locais com correção de âncoras e hrefs.
Foco: processar HTMLs locais, corrigir âncoras/hrefs e retornar conteúdo para embedding.
"""

import os
import re
import logging
from typing import Optional, Set
from urllib.parse import urlparse
from scielo_classic_website.htmlbody.html_body import HTMLContent


class HTMLEmbedder:
    """Navegador recursivo para HTMLs locais com correção de âncoras e hrefs.
    
    Função principal: Navegar entre HTMLs locais, corrigir âncoras e hrefs
    adicionando prefixos baseados no nome do arquivo, e retornar o conteúdo
    corrigido para embedding no HTML principal.
    
    A identificação de assets (PDF, etc.) ocorrerá depois, no HTML principal
    com todo o conteúdo já embedado.
    """
    
    def __init__(self, journal_acron_folder, file_reader, processed):
        """
        Inicializa o navegador.
        
        Args:
            file_reader: callable para ler arquivos HTML
            journal_acron_folder: Acrônimo da revista para identificar arquivos locais
        """
        self.journal_acron_folder = journal_acron_folder
        self.file_reader = file_reader or None
        self.process_filenames = processed

    def _is_local_html_file(self, href: str) -> bool:
        """
        Determina se um arquivo HTML é local baseado na presença de acrônimo entre barras.
        
        Args:
            href: Caminho para o arquivo HTML
            
        Returns:
            True se for arquivo local (contém /acrônimo/), False caso contrário
        """
        # Normaliza barras
        normalized_href = href.replace('\\', '/')

        if self.journal_acron_folder not in normalized_href:
            return False
        
        # URLs absolutas não são locais
        if normalized_href.startswith('http://') or normalized_href.startswith('https://'):
            return False
        
        # Verifica padrão /acrônimo/ no caminho
        pattern = r'.*/([a-zA-Z]+)/[^/]*\.html?(?:#.*)?$'
        return bool(re.search(pattern, normalized_href))
    
    def get_html_to_embed(self, href: str, raw_data=None) -> Optional[str]:
        """
        Processa um HTML local navegando recursivamente e corrigindo âncoras/hrefs.
        
        Args:
            href: Caminho para o arquivo HTML local
            raw_data: Dados brutos para acessar arquivos (opcional)
            
        Returns:
            Node
        """
        if not self._is_local_html_file(href):
            logging.info(f"Arquivo {href} não é local - não será processado")
            return None
        
        anchor_prefix, ext = os.path.splitext(os.path.basename(href))

        # Evita loops recursivos
        if anchor_prefix in self.process_filenames:
            logging.warning(f"Arquivo {href} já processado - evitando loop")
            return f"<!-- LOOP DETECTADO: {href} -->"

        try:
            # Lê o conteúdo HTML
            html_content = self._read_html_file(href, raw_data)
            if not html_content:
                return None
        except Exception as e:
            logging.exception(e)
            return None
        
        try:            
            html_body = HTMLContent(html_content)
            body_node = html_body.tree.find('body')
            if body_node is None:
                logging.warning(f"Nenhum corpo encontrado em {href}")
                return None
        except Exception as e:
            logging.exception(e)
            return None
        
        body_node.tag = "embedded-html"
        body_node.set("path", href)
        
        self.add_anchor_prefix(body_node, href, anchor_prefix)
        self.process_filenames.add(anchor_prefix)

        self.process_html_file(body_node)
        return body_node
    
    def add_anchor_prefix(self, body_node, href, anchor_prefix):
        for node in body_node.xpath('.//a[@name]'):
            name = node.get('name')
            new_name = anchor_prefix + name
            node.set("name", new_name)
        for a_href in body_node.xpath(f'.//a[@href="{href}"]'):
            a_href.set("href", f"#{anchor_prefix}")
            a_href.set("original-href", href)

    def process_html_file(self, body_node):
        for node in body_node.xpath('.//img[@src]|.//a[@src]'):
            node.set("href", node.get("src"))

        for a_href in body_node.xpath('.//a[@href]'):
            href = (a_href.get('href') or "").strip()
            if not self._is_local_html_file(href):
                continue
            parts = href.split("#")
            path = parts[0]
            anchor = ""
            if len(parts) > 1:
                anchor = parts[-1]
            new_anchor_prefix, ext = os.path.splitext(os.path.basename(path))
            new_name = f"{new_anchor_prefix}{anchor}"
            new_anchor = f"#{new_name}"

            if new_anchor_prefix in self.process_filenames:
                a_href.set("href", new_anchor)
                a_href.set("original-href", href)
                logging.info(f"HTML local já processado: {href}")
                continue
            try:
                # Navega e processa o HTML local recursivamente
                corrected_html = self.get_html_to_embed(path)
            except Exception as e:
                logging.exception(e)
                corrected_html = None
            if not corrected_html:
                logging.warning(f"Não foi possível processar HTML: {path}")
                continue
            # Cria elemento para o conteúdo embedado
            parent = a_href.getparent()
            if parent is None:
                continue
            # Cria wrapper com conteúdo corrigido
            parent.addnext(corrected_html)
            a_href.set("href", new_anchor)
            a_href.set("original-href", href)
            self.process_filenames.add(new_name)   

    def _read_html_file(self, href: str, raw_data=None) -> Optional[str]:
        """
        Lê o conteúdo do arquivo HTML.
        
        Args:
            href: Caminho para o arquivo HTML
            raw_data: Dados brutos para acessar arquivos (opcional)
            
        Returns:
            Conteúdo do arquivo HTML ou None se erro
        """
        try:
            if not self.file_reader:
                return None
            
            return self.file_reader(href, self.journal_acron_folder)
                
        except Exception as e:
            logging.error(f"Erro ao ler arquivo HTML {href}: {e}")
            return None


def get_html_to_embed(href, journal_acron_folder, file_reader, processed):
    """
    """
    try:
        html_embedder = HTMLEmbedder(journal_acron_folder, file_reader, processed)
        return html_embedder.get_html_to_embed(href)
    except Exception as e:
        logging.exception(e)
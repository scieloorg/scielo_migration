from thefuzz import fuzz, process
import re
from unidecode import unidecode


section_matcher = SectionMatcher()


def get_sectype(section_title):
    return section_matcher.match_multiplas_secoes(section_title)


class SectionMatcher:
    """
    Classe para fazer match fuzzy entre textos e seções padronizadas de artigos científicos.
    """
    
    def __init__(self, limiar=75):
        """
        Inicializa o matcher com as seções padrão.
        
        Args:
            limiar: Score mínimo para considerar um match válido (0-100)
        """
        self.limiar = limiar
        
        # Seções padrão
        self.secoes_padrao = [
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
        
        # Dicionário com variações conhecidas para cada seção
        # Isso ajuda a melhorar o match
        self.variacoes_conhecidas = {
            'cases': [
                'cases', 'case studies', 'case study', 'casos', 'case reports',
                'case presentation', 'case description', 'clinical cases',
                'casos clínicos', 'estudo de caso', 'estudos de caso'
            ],
            'conclusions': [
                'conclusions', 'conclusion', 'conclusão', 'conclusões',
                'conclusiones', 'conclusión', 'final remarks', 'concluding remarks',
                'summary and conclusions', 'final considerations', 'considerações finais'
            ],
            'data-availability': [
                'data availability', 'data-availability', 'data availability statement',
                'disponibilidade de dados', 'available data', 'data access',
                'data sharing', 'dados disponíveis', 'availability of data'
            ],
            'discussion': [
                'discussion', 'discussão', 'discusión', 'discussions',
                'discussion and conclusion', 'results and discussion',
                'discussão e conclusão', 'resultados e discussão'
            ],
            'intro': [
                'introduction', 'intro', 'introdução', 'introducción',
                'introduccion', 'introduzione', 'einführung', 'einleitung',
                'background', 'background and introduction', 'apresentação'
            ],
            'materials': [
                'materials', 'material', 'materiais', 'materiales',
                'materials and methods', 'material and methods',
                'materiais e métodos', 'experimental materials'
            ],
            'methods': [
                'methods', 'method', 'methodology', 'métodos', 'método',
                'metodologia', 'metodología', 'methodologies', 'experimental',
                'experimental procedures', 'procedimentos', 'materials and methods'
            ],
            'results': [
                'results', 'result', 'resultados', 'resultado', 'findings',
                'results and discussion', 'resultados e discussão',
                'experimental results', 'outcomes', 'resultados experimentais'
            ],
            'subjects': [
                'subjects', 'subject', 'participants', 'patients',
                'sujeitos', 'participantes', 'pacientes', 'population',
                'study population', 'população', 'sample', 'amostra'
            ],
            'supplementary-material': [
                'supplementary material', 'supplementary-material',
                'supplementary materials', 'supplemental material',
                'material suplementar', 'materiais suplementares',
                'supporting information', 'additional material',
                'appendix', 'apêndice', 'anexo', 'anexos', 'supplement'
            ],
            'transcript': [
                'transcript', 'transcription', 'transcrição',
                'transcripción', 'transcripts', 'transcrições',
                'transcribed text', 'texto transcrito'
            ]
        }
        
        # Cria um mapeamento reverso para busca eficiente
        self._criar_mapeamento_reverso()
    
    def _criar_mapeamento_reverso(self):
        """Cria um mapeamento de variações para seções padrão."""
        self.mapa_variacoes = {}
        for secao, variacoes in self.variacoes_conhecidas.items():
            for variacao in variacoes:
                variacao_norm = self._normalizar_texto(variacao)
                self.mapa_variacoes[variacao_norm] = secao
    
    def _normalizar_texto(self, texto):
        """
        Normaliza o texto removendo acentos, caracteres especiais e padronizando.
        
        Args:
            texto: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        # Remove acentos
        texto = unidecode(texto.lower().strip())
        
        # Remove hífens e underscores, substitui por espaço
        texto = re.sub(r'[-_]', ' ', texto)
        
        # Remove múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        
        # Remove caracteres especiais mantendo apenas letras, números e espaços
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        
        return texto.strip()
    
    def match(self, texto, retornar_score=False):
        """
        Encontra a melhor correspondência para o texto fornecido.
        
        Args:
            texto: Texto de entrada para fazer match
            retornar_score: Se True, retorna também o score do match
            
        Returns:
            Seção padrão correspondente ou None se não houver match bom o suficiente
            Se retornar_score=True, retorna tupla (seção, score)
        """
        texto_norm = self._normalizar_texto(texto)
        
        # 1. Primeiro tenta match exato com variações conhecidas
        if texto_norm in self.mapa_variacoes:
            secao = self.mapa_variacoes[texto_norm]
            return (secao, 100.0) if retornar_score else secao
        
        # 2. Tenta fuzzy match com todas as variações conhecidas
        todas_variacoes = list(self.mapa_variacoes.keys())
        
        if todas_variacoes:
            melhor_match = process.extractOne(
                texto_norm,
                todas_variacoes,
                scorer=fuzz.ratio
            )
            
            if melhor_match and melhor_match[1] >= self.limiar:
                secao = self.mapa_variacoes[melhor_match[0]]
                return (secao, melhor_match[1]) if retornar_score else secao
        
        # 3. Se não encontrou nas variações, tenta direto com as seções padrão
        # (útil para casos onde o texto já está próximo do padrão)
        secoes_normalizadas = [self._normalizar_texto(s) for s in self.secoes_padrao]
        
        melhor_match = process.extractOne(
            texto_norm,
            secoes_normalizadas,
            scorer=fuzz.ratio
        )
        
        if melhor_match and melhor_match[1] >= self.limiar:
            # Encontra a seção original correspondente
            idx = secoes_normalizadas.index(melhor_match[0])
            secao = self.secoes_padrao[idx]
            return (secao, melhor_match[1]) if retornar_score else secao
        
        return (None, 0.0) if retornar_score else None
    
    def match_multiplos(self, textos):
        """
        Faz match de múltiplos textos de uma vez.
        
        Args:
            textos: Lista de textos para fazer match
            
        Returns:
            Dicionário com texto original como chave e seção correspondente como valor
        """
        resultados = {}
        for texto in textos:
            resultados[texto] = self.match(texto)
        return resultados
    
    def sugerir_matches(self, texto, num_sugestoes=3):
        """
        Retorna múltiplas sugestões de match com seus scores.
        
        Args:
            texto: Texto de entrada
            num_sugestoes: Número de sugestões a retornar
            
        Returns:
            Lista de tuplas (seção, score) ordenada por score decrescente
        """
        texto_norm = self._normalizar_texto(texto)
        
        # Coleta todos os possíveis matches
        candidatos = {}
        
        # Testa com variações conhecidas
        todas_variacoes = list(self.mapa_variacoes.keys())
        if todas_variacoes:
            matches = process.extract(
                texto_norm,
                todas_variacoes,
                scorer=fuzz.ratio,
                limit=num_sugestoes * 2  # Pega mais para depois filtrar duplicatas
            )
            
            for variacao, score in matches:
                secao = self.mapa_variacoes[variacao]
                if secao not in candidatos or score > candidatos[secao]:
                    candidatos[secao] = score
        
        # Testa direto com seções padrão
        secoes_normalizadas = [self._normalizar_texto(s) for s in self.secoes_padrao]
        matches_diretos = process.extract(
            texto_norm,
            secoes_normalizadas,
            scorer=fuzz.ratio,
            limit=num_sugestoes
        )
        
        for secao_norm, score in matches_diretos:
            idx = secoes_normalizadas.index(secao_norm)
            secao = self.secoes_padrao[idx]
            if secao not in candidatos or score > candidatos[secao]:
                candidatos[secao] = score
        
        # Ordena por score e retorna top N
        sugestoes = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)
        return sugestoes[:num_sugestoes]
    
    def ajustar_limiar(self, novo_limiar):
        """
        Ajusta o limiar de score mínimo para matches.
        
        Args:
            novo_limiar: Novo valor de limiar (0-100)
        """
        if 0 <= novo_limiar <= 100:
            self.limiar = novo_limiar
        else:
            raise ValueError("Limiar deve estar entre 0 e 100")
    
    def match_multiplas_secoes(self, texto, limiar_secundario=60, max_secoes=3):
        """
        Retorna múltiplas seções concatenadas quando o texto pode corresponder a mais de uma.
        Por exemplo: "Materials and Methods" retorna "materials|methods"
        
        Args:
            texto: Texto de entrada para fazer match
            limiar_secundario: Score mínimo para incluir seções adicionais
            max_secoes: Número máximo de seções a concatenar
            
        Returns:
            String com seções concatenadas por | ou None se não houver matches
        """
        texto_norm = self._normalizar_texto(texto)
        
        # Lista para armazenar seções encontradas
        secoes_encontradas = []
        scores_secoes = {}
        
        # Verifica se o texto contém palavras-chave de múltiplas seções
        palavras_texto = set(texto_norm.split())
        
        # Analisa cada seção padrão
        for secao in self.secoes_padrao:
            score_secao = 0
            matches_variacao = []
            
            # Verifica todas as variações da seção
            for variacao in self.variacoes_conhecidas.get(secao, []):
                variacao_norm = self._normalizar_texto(variacao)
                palavras_variacao = set(variacao_norm.split())
                
                # Calcula score baseado em palavras em comum
                palavras_comuns = palavras_texto.intersection(palavras_variacao)
                if palavras_comuns:
                    # Score baseado na proporção de palavras encontradas
                    score_palavras = len(palavras_comuns) * 100 / max(len(palavras_variacao), 1)
                    
                    # Também usa fuzzy matching
                    score_fuzzy = fuzz.partial_ratio(variacao_norm, texto_norm)
                    
                    # Combina os scores
                    score_atual = max(score_palavras, score_fuzzy)
                    
                    if score_atual > score_secao:
                        score_secao = score_atual
                        matches_variacao.append((variacao, score_atual))
            
            # Se a seção teve um bom score, adiciona à lista
            if score_secao >= limiar_secundario:
                scores_secoes[secao] = score_secao
        
        # Ordena seções por score
        secoes_ordenadas = sorted(scores_secoes.items(), key=lambda x: x[1], reverse=True)
        
        # Seleciona as melhores seções (até max_secoes)
        for secao, score in secoes_ordenadas[:max_secoes]:
            if score >= limiar_secundario:
                secoes_encontradas.append(secao)
        
        # Se não encontrou nenhuma seção com o método acima, tenta o match simples
        if not secoes_encontradas:
            secao_simples = self.match(texto)
            if secao_simples:
                return secao_simples
            return None
        
        # Remove duplicatas mantendo a ordem
        secoes_unicas = []
        for secao in secoes_encontradas:
            if secao not in secoes_unicas:
                secoes_unicas.append(secao)
        
        # Ordena as seções encontradas pela ordem em que aparecem em secoes_padrao
        # para manter consistência
        secoes_unicas.sort(key=lambda x: self.secoes_padrao.index(x))
        
        return '|'.join(secoes_unicas)


# ===== EXEMPLOS DE USO =====

if __name__ == "__main__":
    # Inicializa o matcher
    matcher = SectionMatcher(limiar=75)
    
    print("=" * 60)
    print("TESTE DE MATCH SIMPLES")
    print("=" * 60)
    
    # Testes com diferentes entradas
    testes = [
        "Introduction",
        "INTRODUÇÃO",
        "Introducción",
        "Materials and Methods",
        "Métodos",
        "RESULTS AND DISCUSSION",
        "Conclusões",
        "Supplementary Materials",
        "Case Study",
        "Data Availability Statement",
        "Transcription",
        "Patient Population",
        "Final Considerations",
        "Metodologia",
        "ABSTRACT",  # Não deve fazer match
        "References",  # Não deve fazer match
    ]
    
    for texto in testes:
        resultado = matcher.match(texto)
        print(f"'{texto}' → {resultado if resultado else 'Sem correspondência'}")
    
    print("\n" + "=" * 60)
    print("TESTE COM SCORES")
    print("=" * 60)
    
    # Testes retornando scores
    testes_com_score = [
        "Intro",
        "Introduction and Background",
        "Materials & Methods",
        "Discusion",  # Com erro de digitação
        "Conclussion",  # Com erro de digitação
    ]
    
    for texto in testes_com_score:
        resultado, score = matcher.match(texto, retornar_score=True)
        if resultado:
            print(f"'{texto}' → {resultado} (score: {score:.1f}%)")
        else:
            print(f"'{texto}' → Sem correspondência")
    
    print("\n" + "=" * 60)
    print("SUGESTÕES MÚLTIPLAS")
    print("=" * 60)
    
    # Teste de sugestões múltiplas
    textos_ambiguos = [
        "Material",
        "Discussion and Conclusion",
        "Study Participants",
        "Métodos Experimentais"
    ]
    
    for texto in textos_ambiguos:
        print(f"\nSugestões para '{texto}':")
        sugestoes = matcher.sugerir_matches(texto, num_sugestoes=3)
        for secao, score in sugestoes:
            print(f"  - {secao}: {score:.1f}%")
    
    print("\n" + "=" * 60)
    print("TESTE COM LIMIAR AJUSTADO")
    print("=" * 60)
    
    # Teste com diferentes limiares
    texto_teste = "Concluzion"  # Erro de digitação proposital
    
    for limiar in [90, 75, 60]:
        matcher.ajustar_limiar(limiar)
        resultado = matcher.match(texto_teste)
        print(f"Limiar {limiar}: '{texto_teste}' → {resultado if resultado else 'Sem correspondência'}")
    
    print("\n" + "=" * 60)
    print("TESTE DE MÚLTIPLAS SEÇÕES")
    print("=" * 60)
    
    # Teste do novo método para múltiplas seções
    textos_multiplos = [
        "Materials and Methods",
        "Materiais e Métodos",
        "Results and Discussion",
        "Resultados e Discussão",
        "Introduction and Background",
        "Methods and Materials",
        "Discussion and Conclusions",
        "Subjects and Methods",
        "Conclusion",  # Deve retornar apenas uma seção
        "Data Availability and Supplementary Materials"
    ]
    
    print("\nTextos que correspondem a múltiplas seções:")
    for texto in textos_multiplos:
        resultado = matcher.match_multiplas_secoes(texto)
        print(f"  '{texto}' → {resultado if resultado else 'Sem correspondência'}")
    
    print("\n" + "=" * 60)
    print("PROCESSAMENTO EM LOTE")
    print("=" * 60)
    
    # Processa múltiplos textos de uma vez
    secoes_documento = [
        "Abstract",
        "1. Introduction",
        "2. Materials and Methods",
        "3. Results",
        "4. Discussion",
        "5. Conclusions",
        "References"
    ]
    
    matcher.ajustar_limiar(75)
    resultados_lote = matcher.match_multiplos(secoes_documento)
    
    print("\nMapeamento de seções do documento:")
    for texto_original, secao_padrao in resultados_lote.items():
        if secao_padrao:
            print(f"  '{texto_original}' → {secao_padrao}")
        else:
            print(f"  '{texto_original}' → [não mapeado]")
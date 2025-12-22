
# Mapeamento bidirecional: ID prefix <-> ref-type <-> element-name
ID_PREFIX_TO_REF_TYPE = {
    "aff": "aff",
    "app": "app",
    "c": "corresp",
    "e": "disp-formula",
    "f": "fig",
    "gf": "graphic",
    "suppl": "supplementary-material",
    "m": "math",
    "fn": "fn",
    "anf": "author-notes-fn",  # author-notes fn
    "TFN": "table-fn",
    "md": "media",
    "B": "bibr",
    "r": "related-article",
    "vs": "visual-abstract",
    "sec": "sec",
    "TR": "transcript-sec",
    "S": "sub-article",
    "t": "table",
    "box": "boxed-text",
    "list": "list",
    "contrib": "contrib",
}

REF_TYPE_TO_ID_PREFIX = {v: k for k, v in ID_PREFIX_TO_REF_TYPE.items()}

# Mapeamento ref-type para element-name
REF_TYPE_TO_ELEMENT = {
    "aff": "aff",
    "app": "app",
    "author-notes": "author-notes",
    "bibr": "ref",
    "bio": "bio",
    "boxed-text": "boxed-text",
    "contrib": "contrib",
    "corresp": "corresp",
    "disp-formula": "disp-formula",
    "inline-formula": "inline-formula",
    "fig": "fig",
    "fn": "fn",
    "author-notes-fn": "fix-author-notes-fn",
    "graphic": "graphic",
    "inline-graphic": "inline-graphic",
    "list": "list",
    "math": "mml:math",
    "media": "media",
    "inline-media": "inline-media",
    "related-article": "related-article",
    "sec": "sec",
    "sub-article": "sub-article",
    "response": "response",
    "supplementary-material": "supplementary-material",
    "table-fn": "fix-table-wrap-foot-fn",
    "table": "table-wrap",
    "transcript-sec": "fix-sec-transcript",
    "visual-abstract": "fix-visual-abstract",
}

# Padrões de texto para identificação em múltiplos idiomas
# Padrões de texto para identificação em múltiplos idiomas
TEXT_PATTERNS = {
    # Figuras
    "fig": [
        # Inglês
        r"(?i)^fig\.?(?:\s*\d+)?$",  # fig, fig., fig 1, FIG. 2
        r"(?i)^figure(?:\s*\d+)?$",  # Figure, figure 3, FIGURE 4
        # Português
        r"(?i)^figura(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^fig\.?(?:\s*\d+)?$",
        r"(?i)^figura(?:\s*\d+)?$",
        r"(?i)^gráfico(?:\s*\d+)?$",
        # Francês
        r"(?i)^fig\.?(?:\s*\d+)?$",
        r"(?i)^figure(?:\s*\d+)?$",
        r"(?i)^schéma(?:\s*\d+)?$",
        # Alemão
        r"(?i)^abb\.?(?:\s*\d+)?$",
        r"(?i)^abbildung(?:\s*\d+)?$",
        r"(?i)^bild(?:\s*\d+)?$",
        # Africâner
        r"(?i)^fig\.?(?:\s*\d+)?$",
        r"(?i)^figuur(?:\s*\d+)?$",
        r"(?i)^beeld(?:\s*\d+)?$"
    ],
    # Tabelas
    "table": [
        # Inglês
        r"(?i)^tab\.?(?:\s*\d+)?$",  # tab, tab., Tab 1, TAB. 2
        r"(?i)^table(?:\s*\d+)?$",  # Table, table 3, TABLE 4
        # Português
        r"(?i)^tabela(?:\s*\d+)?$",
        r"(?i)^quadro(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^tabla(?:\s*\d+)?$",
        r"(?i)^cuadro(?:\s*\d+)?$",
        # Francês
        r"(?i)^tableau(?:\s*\d+)?$",
        r"(?i)^tabl\.?(?:\s*\d+)?$",
        # Alemão
        r"(?i)^tabelle(?:\s*\d+)?$",
        r"(?i)^tab\.?(?:\s*\d+)?$",
        r"(?i)^tafel(?:\s*\d+)?$",
        # Africâner
        r"(?i)^tabel(?:\s*\d+)?$",
        r"(?i)^tab\.?(?:\s*\d+)?$"
    ],
    # Referências bibliográficas
    "bibr": [
        # Padrões de autor em múltiplos idiomas
        r"^[A-Z][a-z]+\s+et\s+al\.?,?\s*\d{4}",  # Silva et al., 2024
        r"^[A-Z][a-z]+\s+y\s+cols?\.?,?\s*\d{4}",  # García y col., 2024 (espanhol)
        r"^[A-Z][a-z]+\s+e\s+cols?\.?,?\s*\d{4}",  # Silva e col., 2024 (português)
        r"^[A-Z][a-z]+\s+et\s+coll?\.?,?\s*\d{4}",  # Dupont et coll., 2024 (francês)
        r"^[A-Z][a-z]+\s+u\.?\s*a\.?,?\s*\d{4}",  # Schmidt u.a., 2024 (alemão)
        r"^[A-Z][a-z]+\s+en\s+andere?,?\s*\d{4}",  # Van Der Merwe en ander, 2024 (africâner)
        r"^[A-Z][a-z]+\s+&\s+[A-Z][a-z]+",  # Silva & Santos
        r"^[A-Z][a-z]+\s+y\s+[A-Z][a-z]+",  # García y López (espanhol)
        r"^[A-Z][a-z]+\s+e\s+[A-Z][a-z]+",  # Silva e Santos (português)
        r"^[A-Z][a-z]+\s+et\s+[A-Z][a-z]+",  # Dupont et Martin (francês)
        r"^[A-Z][a-z]+\s+und\s+[A-Z][a-z]+",  # Schmidt und Müller (alemão)
        r"^[A-Z][a-z]+\s+en\s+[A-Z][a-z]+",  # Van Der Merwe en Botha (africâner)
        r"^[A-Z][a-z]+,?\s*\d{4}",  # Silva, 2024
        r"^\([A-Z][a-z]+.*\d{4}\)",  # (Silva, 2024)
        r"^\[\d+\]$",  # [1]
        # r"^\(\d+\)$",  # (1) - REMOVIDO, mantido apenas em disp-formula
        r"^\d+\s*-\s*\d+$",  # 1-3
        r"^\d+,\s*\d+",  # 1, 2
    ],
    # Equações/Fórmulas
    "disp-formula": [
        # Inglês
        r"(?i)^eq\.?(?:\s*\d+)?$",  # eq, eq., Eq 1, EQ. 2
        r"(?i)^equation(?:\s*\d+)?$",  # Equation, equation 3, EQUATION 4
        # Português
        r"(?i)^eq\.?(?:\s*\d+)?$",
        r"(?i)^equação(?:\s*\d+)?$",
        r"(?i)^fórmula(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^ec\.?(?:\s*\d+)?$",
        r"(?i)^ecuación(?:\s*\d+)?$",
        r"(?i)^fórmula(?:\s*\d+)?$",
        # Francês
        r"(?i)^éq\.?(?:\s*\d+)?$",
        r"(?i)^équation(?:\s*\d+)?$",
        r"(?i)^formule(?:\s*\d+)?$",
        # Alemão
        r"(?i)^gl\.?(?:\s*\d+)?$",
        r"(?i)^gleichung(?:\s*\d+)?$",
        r"(?i)^formel(?:\s*\d+)?$",
        # Africâner
        r"(?i)^vgl\.?(?:\s*\d+)?$",
        r"(?i)^vergelyking(?:\s*\d+)?$",
        r"(?i)^formule(?:\s*\d+)?$",
        r"^\(\d+\)$"  # (1) quando em contexto matemático
    ],
    # Fórmulas inline
    "inline-formula": [
        r"(?i)^inline\s*eq\.?(?:\s*\d+)?$",  # inline eq, inline eq., inline eq 1
        r"(?i)^inline\s*formula(?:\s*\d+)?$"  # inline formula, INLINE FORMULA 2
    ],
    # Notas de rodapé
    "fn": [
        # r"^[*‡§¶#]+$",  # Símbolos especiais - REMOVIDO
        # r"^[a-z]$",  # Letra minúscula única - REMOVIDO
        # Inglês
        r"(?i)^note(?:\s*\d+)?$",  # note, Note, NOTE 1
        r"(?i)^footnote(?:\s*\d+)?$",  # footnote, Footnote 2, FOOTNOTE 3
        # Português
        r"(?i)^nota(?:\s*\d+)?$",
        r"(?i)^nota\s+de\s+rodapé(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^nota(?:\s*\d+)?$",
        r"(?i)^nota\s+al\s+pie(?:\s*\d+)?$",
        # Francês
        r"(?i)^note(?:\s*\d+)?$",
        r"(?i)^note\s+de\s+bas\s+de\s+page(?:\s*\d+)?$",
        # Alemão
        r"(?i)^anm\.?(?:\s*\d+)?$",
        r"(?i)^anmerkung(?:\s*\d+)?$",
        r"(?i)^fußnote(?:\s*\d+)?$",
        # Africâner
        r"(?i)^voetnota(?:\s*\d+)?$",
        r"(?i)^nota(?:\s*\d+)?$",
    ],
    # Notas de author-notes (autor falecido, etc.)
    "author-notes-fn": [
        r"^†+$",  # †, ††, †††
        # Padrões específicos para notas de autor
        r"(?i)^deceased",  # deceased, Deceased, DECEASED
        r"(?i)^falecido",
        r"(?i)^fallecido",  # Espanhol
        r"(?i)^décédé",     # Francês
        r"(?i)^verstorben", # Alemão
        r"(?i)^oorlede",    # Africâner
        r"(?i)^in\s+memoriam",
        r"(?i)^author\s+note",
        r"(?i)^nota\s+do\s+autor",
        r"(?i)^nota\s+del\s+autor",  # Espanhol
        r"(?i)^note\s+de\s+l'auteur",  # Francês
        r"(?i)^autornotiz",  # Alemão
        r"(?i)^outeurnota",  # Africâner
    ],
    # Notas de rodapé de tabela
    "table-fn": [
        r"(?i)^table\s*note(?:\s*\d+)?$",  # table note, Table Note 1, TABLE NOTE 2
        r"(?i)^nota\s+de\s+tabela(?:\s*\d+)?$",  # nota de tabela, Nota de Tabela 1
        r"(?i)^nota\s+de\s+tabla(?:\s*\d+)?$",  # Espanhol
        r"(?i)^note\s+de\s+tableau(?:\s*\d+)?$",  # Francês
        r"(?i)^tabellennote(?:\s*\d+)?$",  # Alemão
        r"(?i)^tabelnota(?:\s*\d+)?$",  # Africâner
        r"(?i)^tn(?:\s*\d+)?$",
        # r"^[*‡§¶#]+$"  # Em contexto de tabela - REMOVIDO
    ],
    # Seções
    "sec": [
        # Inglês
        r"(?i)^sec\.?(?:\s*\d+)?$",  # sec, sec., Sec 1, SEC. 2
        r"(?i)^section(?:\s*\d+)?$",  # Section, section 3, SECTION 4
        r"(?i)^chapter(?:\s*\d+)?$",
        # Português
        r"(?i)^seção(?:\s*\d+)?$",
        r"(?i)^capítulo(?:\s*\d+)?$",
        r"(?i)^parte(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^sección(?:\s*\d+)?$",
        r"(?i)^sec\.?(?:\s*\d+)?$",
        r"(?i)^capítulo(?:\s*\d+)?$",
        r"(?i)^apartado(?:\s*\d+)?$",
        # Francês
        r"(?i)^section(?:\s*\d+)?$",
        r"(?i)^chapitre(?:\s*\d+)?$",
        r"(?i)^partie(?:\s*\d+)?$",
        # Alemão
        r"(?i)^abschnitt(?:\s*\d+)?$",
        r"(?i)^kapitel(?:\s*\d+)?$",
        r"(?i)^teil(?:\s*\d+)?$",
        # Africâner
        r"(?i)^afdeling(?:\s*\d+)?$",
        r"(?i)^hoofstuk(?:\s*\d+)?$",
        r"(?i)^deel(?:\s*\d+)?$",
        r"(?i)^\d+\.\d+",  # 2.1, 3.2, etc
    ],
    # Apêndices
    "app": [
        # Inglês
        r"(?i)^app\.?(?:\s*[A-Z\d])?$",  # app, app., App A, APP. 1
        r"(?i)^appendix(?:\s*[A-Z\d])?$",  # Appendix, appendix B, APPENDIX 2
        r"(?i)^annex(?:\s*[A-Z\d])?$",
        # Português
        r"(?i)^apêndice(?:\s*[A-Z\d])?$",
        r"(?i)^anexo(?:\s*[A-Z\d])?$",
        # Espanhol
        r"(?i)^apéndice(?:\s*[A-Z\d])?$",
        r"(?i)^anexo(?:\s*[A-Z\d])?$",
        # Francês
        r"(?i)^appendice(?:\s*[A-Z\d])?$",
        r"(?i)^annexe(?:\s*[A-Z\d])?$",
        # Alemão
        r"(?i)^anhang(?:\s*[A-Z\d])?$",
        r"(?i)^anlage(?:\s*[A-Z\d])?$",
        # Africâner
        r"(?i)^bylae(?:\s*[A-Z\d])?$",
        r"(?i)^aanhangsel(?:\s*[A-Z\d])?$"
    ],
    # Material suplementar
    "supplementary-material": [
        # Inglês
        r"(?i)^supp",  # supp, Supp, SUPP
        r"(?i)^supplement",  # supplement, Supplement, SUPPLEMENT
        r"(?i)^additional\s+file(?:\s*\d+)?$",
        r"(?i)^supporting\s+information(?:\s*\d+)?$",
        # Português
        r"(?i)^material\s+suplementar(?:\s*\d+)?$",
        r"(?i)^dados?\s+suplementar(?:es)?(?:\s*\d+)?$",
        r"(?i)^arquivo\s+adicional(?:\s*\d+)?$",
        r"(?i)^informaç(ão|ões)\s+suplementar(?:es)?(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^material\s+suplementario(?:\s*\d+)?$",
        r"(?i)^datos?\s+suplementario(?:s)?(?:\s*\d+)?$",
        r"(?i)^archivo\s+adicional(?:\s*\d+)?$",
        r"(?i)^información\s+suplementaria(?:\s*\d+)?$",
        # Francês
        r"(?i)^matériel\s+supplémentaire(?:\s*\d+)?$",
        r"(?i)^données?\s+supplémentaires?(?:\s*\d+)?$",
        r"(?i)^fichier\s+supplémentaire(?:\s*\d+)?$",
        r"(?i)^information\s+supplémentaire(?:\s*\d+)?$",
        # Alemão
        r"(?i)^ergänzende[sn]?\s+material(?:\s*\d+)?$",
        r"(?i)^zusätzliche[sn]?\s+datei(?:\s*\d+)?$",
        r"(?i)^supplementäre[sn]?\s+information(?:\s*\d+)?$",
        # Africâner
        r"(?i)^aanvullende\s+materiaal(?:\s*\d+)?$",
        r"(?i)^bykomende\s+lêer(?:\s*\d+)?$",
        r"(?i)^addisionele\s+inligting(?:\s*\d+)?$",
        r"(?i)^s\d+$"  # S1, S2, etc
    ],
    # Sub-artigo
    "sub-article": [
        # Inglês
        r"(?i)^sub-?article(?:\s*\d+)?$",  # sub-article, subarticle, Sub-Article 1
        r"(?i)^response(?:\s*\d+)?$",  # response, Response, RESPONSE 2
        r"(?i)^reply(?:\s*\d+)?$",
        r"(?i)^comment(?:\s*\d+)?$",
        # Português
        r"(?i)^sub-?artigo(?:\s*\d+)?$",
        r"(?i)^resposta(?:\s*\d+)?$",
        r"(?i)^réplica(?:\s*\d+)?$",
        r"(?i)^comentário(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^sub-?artículo(?:\s*\d+)?$",
        r"(?i)^respuesta(?:\s*\d+)?$",
        r"(?i)^réplica(?:\s*\d+)?$",
        r"(?i)^comentario(?:\s*\d+)?$",
        # Francês
        r"(?i)^sous-?article(?:\s*\d+)?$",
        r"(?i)^réponse(?:\s*\d+)?$",
        r"(?i)^réplique(?:\s*\d+)?$",
        r"(?i)^commentaire(?:\s*\d+)?$",
        # Alemão
        r"(?i)^unterartikel(?:\s*\d+)?$",
        r"(?i)^antwort(?:\s*\d+)?$",
        r"(?i)^erwiderung(?:\s*\d+)?$",
        r"(?i)^kommentar(?:\s*\d+)?$",
        # Africâner
        r"(?i)^sub-?artikel(?:\s*\d+)?$",
        r"(?i)^antwoord(?:\s*\d+)?$",
        r"(?i)^repliek(?:\s*\d+)?$",
        r"(?i)^kommentaar(?:\s*\d+)?$"
    ],
    # Caixas de texto
    "boxed-text": [
        # Inglês
        r"(?i)^box(?:\s*\d+)?$",  # box, Box, BOX 1
        r"(?i)^panel(?:\s*\d+)?$",  # panel, Panel 2, PANEL 3
        # Português
        r"(?i)^quadro(?:\s*\d+)?$",
        r"(?i)^caixa(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^cuadro(?:\s*\d+)?$",
        r"(?i)^recuadro(?:\s*\d+)?$",
        r"(?i)^caja(?:\s*\d+)?$",
        # Francês
        r"(?i)^encadré(?:\s*\d+)?$",
        r"(?i)^boîte(?:\s*\d+)?$",
        r"(?i)^cadre(?:\s*\d+)?$",
        # Alemão
        r"(?i)^kasten(?:\s*\d+)?$",
        r"(?i)^rahmen(?:\s*\d+)?$",
        r"(?i)^textbox(?:\s*\d+)?$",
        # Africâner
        r"(?i)^kassie(?:\s*\d+)?$",
        r"(?i)^raam(?:\s*\d+)?$",
        r"(?i)^blokkie(?:\s*\d+)?$"
    ],
    # Afiliações
    "aff": [
        # r"^[a-z]$",  # Letra minúscula única - REMOVIDO
        # r"^[*‡§¶#]+$",  # Símbolos - REMOVIDO
        # Inglês
        r"(?i)^aff\.?(?:\s*\d+)?$",  # aff, aff., Aff 1, AFF. 2
        r"(?i)^affiliation(?:\s*\d+)?$",  # affiliation, Affiliation 3
        # Português
        r"(?i)^afiliação(?:\s*\d+)?$",
        r"(?i)^filiação(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^afiliación(?:\s*\d+)?$",
        r"(?i)^filiación(?:\s*\d+)?$",
        # Francês
        r"(?i)^affiliation(?:\s*\d+)?$",
        # Alemão
        r"(?i)^zugehörigkeit(?:\s*\d+)?$",
        r"(?i)^affiliation(?:\s*\d+)?$",
        # Africâner
        r"(?i)^affiliasie(?:\s*\d+)?$",
        r"(?i)^verbintenis(?:\s*\d+)?$"
    ],
    # Correspondência
    "corresp": [
        # r"^[*]$",  # Apenas asterisco - REMOVIDO
        r"(?i)^correspond",  # correspond, Correspond, CORRESPONDING
        r"(?i)^e-?mail",  # email, e-mail, Email, E-MAIL
        r"(?i)^corresp\.?(?:\s*\d+)?$",
        # Português
        r"(?i)^correspondência",
        r"(?i)^autor\s+correspondente",
        # Espanhol
        r"(?i)^correspondencia",
        r"(?i)^autor\s+para\s+correspondencia",
        # Francês
        r"(?i)^correspondance",
        r"(?i)^auteur\s+correspondant",
        # Alemão
        r"(?i)^korrespondenz",
        r"(?i)^korrespondierender\s+autor",
        # Africâner
        r"(?i)^korrespondensie",
        r"(?i)^korresponderende\s+outeur"
    ],
    # Contribuidores
    "contrib": [
        r"^[A-Z]{2,}$",  # JMS, ABC, XYZ
        r"^[A-Z][A-Z\s]+[A-Z]$",  # J M S, A B C
        # Termos em múltiplos idiomas
        r"(?i)^autor(?:\s*\d+)?$",
        r"(?i)^author(?:\s*\d+)?$",
        r"(?i)^auteur(?:\s*\d+)?$",  # Francês
        r"(?i)^autor(?:\s*\d+)?$",  # Espanhol/Português
        r"(?i)^verfasser(?:\s*\d+)?$",  # Alemão
        r"(?i)^outeur(?:\s*\d+)?$",  # Africâner
        r"(?i)^skrywer(?:\s*\d+)?$"  # Africâner
    ],
    # Listas
    "list": [
        # Inglês
        r"(?i)^list(?:\s*\d+)?$",  # list, List, LIST 1
        # Português
        r"(?i)^lista(?:\s*\d+)?$",  # lista, Lista, LISTA 2
        # Espanhol (mesma palavra que português)
        r"(?i)^lista(?:\s*\d+)?$",
        # Francês
        r"(?i)^liste(?:\s*\d+)?$",
        # Alemão
        r"(?i)^liste(?:\s*\d+)?$",
        r"(?i)^auflistung(?:\s*\d+)?$",
        # Africâner
        r"(?i)^lys(?:\s*\d+)?$"
    ],
    # Gráficos
    "graphic": [
        # Inglês
        r"(?i)^graphic(?:\s*\d+)?$",  # graphic, Graphic, GRAPHIC 1
        r"(?i)^image(?:\s*\d+)?$",  # image, Image 2, IMAGE 3
        r"(?i)^illustration(?:\s*\d+)?$",
        # Português
        r"(?i)^gráfico(?:\s*\d+)?$",
        r"(?i)^imagem(?:\s*\d+)?$",
        r"(?i)^ilustração(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^gráfico(?:\s*\d+)?$",
        r"(?i)^imagen(?:\s*\d+)?$",
        r"(?i)^ilustración(?:\s*\d+)?$",
        # Francês
        r"(?i)^graphique(?:\s*\d+)?$",
        r"(?i)^image(?:\s*\d+)?$",
        r"(?i)^illustration(?:\s*\d+)?$",
        # Alemão
        r"(?i)^grafik(?:\s*\d+)?$",
        r"(?i)^bild(?:\s*\d+)?$",
        r"(?i)^illustration(?:\s*\d+)?$",
        # Africâner
        r"(?i)^grafiek(?:\s*\d+)?$",
        r"(?i)^beeld(?:\s*\d+)?$",
        r"(?i)^illustrasie(?:\s*\d+)?$"
    ],
    # Media
    "media": [
        # Inglês
        r"(?i)^media(?:\s*\d+)?$",  # media, Media, MEDIA 1
        r"(?i)^video(?:\s*\d+)?$",  # video, Video 2, VIDEO 3
        r"(?i)^audio(?:\s*\d+)?$",
        r"(?i)^multimedia(?:\s*\d+)?$",
        r"(?i)^movie(?:\s*\d+)?$",
        # Português
        r"(?i)^mídia(?:\s*\d+)?$",
        r"(?i)^vídeo(?:\s*\d+)?$",
        r"(?i)^áudio(?:\s*\d+)?$",
        r"(?i)^multimídia(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^medios?(?:\s*\d+)?$",
        r"(?i)^vídeo(?:\s*\d+)?$",
        r"(?i)^audio(?:\s*\d+)?$",
        r"(?i)^multimedia(?:\s*\d+)?$",
        # Francês
        r"(?i)^média(?:\s*\d+)?$",
        r"(?i)^vidéo(?:\s*\d+)?$",
        r"(?i)^audio(?:\s*\d+)?$",
        r"(?i)^multimédia(?:\s*\d+)?$",
        # Alemão
        r"(?i)^medien(?:\s*\d+)?$",
        r"(?i)^video(?:\s*\d+)?$",
        r"(?i)^audio(?:\s*\d+)?$",
        r"(?i)^multimedia(?:\s*\d+)?$",
        # Africâner
        r"(?i)^media(?:\s*\d+)?$",
        r"(?i)^video(?:\s*\d+)?$",
        r"(?i)^oudio(?:\s*\d+)?$",
        r"(?i)^multimedia(?:\s*\d+)?$"
    ],
    # Artigos relacionados
    "related-article": [
        # Inglês
        r"(?i)^related\s+article(?:\s*\d+)?$",  # related article, Related Article 1
        r"(?i)^see\s+also(?:\s*\d+)?$",  # see also, See Also, SEE ALSO 2
        # Português
        r"(?i)^artigo\s+relacionado(?:\s*\d+)?$",
        r"(?i)^ver\s+também(?:\s*\d+)?$",
        r"(?i)^veja\s+também(?:\s*\d+)?$",
        # Espanhol
        r"(?i)^artículo\s+relacionado(?:\s*\d+)?$",
        r"(?i)^véase\s+también(?:\s*\d+)?$",
        r"(?i)^ver\s+también(?:\s*\d+)?$",
        # Francês
        r"(?i)^article\s+connexe(?:\s*\d+)?$",
        r"(?i)^voir\s+aussi(?:\s*\d+)?$",
        r"(?i)^article\s+lié(?:\s*\d+)?$",
        # Alemão
        r"(?i)^verwandter\s+artikel(?:\s*\d+)?$",
        r"(?i)^siehe\s+auch(?:\s*\d+)?$",
        r"(?i)^zugehöriger\s+artikel(?:\s*\d+)?$",
        # Africâner
        r"(?i)^verwante\s+artikel(?:\s*\d+)?$",
        r"(?i)^sien\s+ook(?:\s*\d+)?$",
        r"(?i)^kyk\s+ook(?:\s*\d+)?$"
    ],
    # MathML
    "math": [
        r"(?i)^math(?:\s*\d+)?$",  # math, Math, MATH 1
        r"(?i)^mathematical\s*expression(?:\s*\d+)?$",  # mathematical expression, Mathematical Expression 2
        r"(?i)^expressão\s+matemática(?:\s*\d+)?$",  # Português
        r"(?i)^expresión\s+matemática(?:\s*\d+)?$",  # Espanhol
        r"(?i)^expression\s+mathématique(?:\s*\d+)?$",  # Francês
        r"(?i)^mathematischer\s+ausdruck(?:\s*\d+)?$",  # Alemão
        r"(?i)^wiskundige\s+uitdrukking(?:\s*\d+)?$"  # Africâner
    ],
    # Padrão genérico para números isolados
    "number": [
        r"^\d+\s*$",  # 1, 2, 123, 9999
    ],
    # Padrão genérico para letras minúsculas isoladas
    "letter": [
        r"^[a-z]$",  # a, b, c, z
    ],
    # Padrão genérico para símbolos especiais
    "symbol": [
        r"^[*‡§¶#]+$",  # *, ‡, §, ¶, #, **, ‡‡, ###
    ],
}

# Padrões de IDs para detecção reversa
ID_PATTERNS = {
    r"^aff\d+": "aff",
    r"^app\d+": "app",
    r"^c\d+": "corresp",
    r"^e\d+": "disp-formula",
    r"^f\d+": "fig",
    r"^gf\d+": "graphic",
    r"^suppl\d+": "supplementary-material",
    r"^m\d+": "math",
    r"^fn\d+": "fn",
    r"^fn[a-z]": "fn",  # fn com letra
    r"^fnast": "fn",  # asterisco
    r"^anf\d+": "author-notes-fn",  # author-notes fn
    r"^fndag": "author-notes-fn",  # cruz (autor falecido)
    r"^TFN\d+": "table-fn",
    r"^md\d+": "media",
    r"^B\d+": "bibr",
    r"^r\d+": "related-article",
    r"^vs\d+": "visual-abstract",
    r"^sec\d+": "sec",
    r"^sec\d+_\d+": "sec",  # seções hierárquicas
    r"^TR\d+": "transcript-sec",
    r"^S\d+": "sub-article",
    r"^t\d+": "table",
    r"^box\d+": "boxed-text",
    r"^list\d+": "list",
    r"^contrib\d+": "contrib",
}


ASSET_TYPE_CONFIG = {
    ".pdf": {
        "asset_type": "pdf",
        "mimetype": "application",
        "mime_subtype": "pdf"
    },
    ".gif": {
        "asset_type": "image",
        "mimetype": "image",
        "mime_subtype": "gif"
    },
    ".jpg": {
        "asset_type": "image",
        "mimetype": "image",
        "mime_subtype": "jpeg"
    },
    ".jpeg": {
        "asset_type": "image",
        "mimetype": "image",
        "mime_subtype": "jpeg"
    },
    ".png": {
        "asset_type": "image",
        "mimetype": "image",
        "mime_subtype": "png"
    },
    ".tiff": {
        "asset_type": "image",
        "mimetype": "image",
        "mime_subtype": "tiff"
    },
    ".bmp": {
        "asset_type": "image",
        "mimetype": "image",
        "mime_subtype": "bmp"
    },
    ".svg": {
        "asset_type": "image",
        "mimetype": "image",
        "mime_subtype": "svg+xml"
    },
    ".mp4": {
        "asset_type": "video",
        "mimetype": "video",
        "mime_subtype": "mp4"
    },
    ".avi": {
        "asset_type": "video",
        "mimetype": "video",
        "mime_subtype": "x-msvideo"
    },
    ".mov": {
        "asset_type": "video",
        "mimetype": "video",
        "mime_subtype": "quicktime"
    },
    ".wmv": {
        "asset_type": "video",
        "mimetype": "video",
        "mime_subtype": "x-ms-wmv"
    },
    ".flv": {
        "asset_type": "video",
        "mimetype": "video",
        "mime_subtype": "x-flv"
    },
    ".mkv": {
        "asset_type": "video",
        "mimetype": "video",
        "mime_subtype": "x-matroska"
    },
    ".mp3": {
        "asset_type": "audio",
        "mimetype": "audio",
        "mime_subtype": "mpeg"
    },
    ".wav": {
        "asset_type": "audio",
        "mimetype": "audio",
        "mime_subtype": "wav"
    },
    ".ogg": {
        "asset_type": "audio",
        "mimetype": "audio",
        "mime_subtype": "ogg"
    },
    ".flac": {
        "asset_type": "audio",
        "mimetype": "audio",
        "mime_subtype": "flac"
    },
    ".htm": {
        "asset_type": "html",
        "mimetype": "text",
        "mime_subtype": "html"
    },
    ".html": {
        "asset_type": "html",
        "mimetype": "text",
        "mime_subtype": "html"
    },
    ".xls": {
        "asset_type": "spreadsheet",
        "mimetype": "application",
        "mime_subtype": "vnd.ms-excel"
    },
    ".xlsx": {
        "asset_type": "spreadsheet",
        "mimetype": "application",
        "mime_subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    },
    ".xlsm": {
        "asset_type": "spreadsheet",
        "mimetype": "application",
        "mime_subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    },
    ".doc": {
        "asset_type": "document",
        "mimetype": "application",
        "mime_subtype": "msword"
    },
    ".docx": {
        "asset_type": "document",
        "mimetype": "application",
        "mime_subtype": "vnd.openxmlformats-officedocument.wordprocessingml.document"
    },
    ".ppt": {
        "asset_type": "presentation",
        "mimetype": "application",
        "mime_subtype": "vnd.ms-powerpoint"
    },
    ".pptx": {
        "asset_type": "presentation",
        "mimetype": "application",
        "mime_subtype": "vnd.openxmlformats-officedocument.presentationml.presentation"
    },
    ".zip": {
        "asset_type": "compressed",
        "mimetype": "application",
        "mime_subtype": "zip"
    },
    ".rar": {
        "asset_type": "compressed",
        "mimetype": "application",
        "mime_subtype": "x-rar-compressed"
    },
    ".7z": {
        "asset_type": "compressed",
        "mimetype": "application",
        "mime_subtype": "x-7z-compressed"
    },
    ".tar": {
        "asset_type": "compressed",
        "mimetype": "application",
        "mime_subtype": "x-tar"
    },
    ".gz": {
        "asset_type": "compressed",
        "mimetype": "application",
        "mime_subtype": "x-tar"
    }
}
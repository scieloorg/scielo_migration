# Padrões para detecção de fn-type em múltiplos idiomas
FN_TYPE_PATTERNS = {
    "abbr": [
        # Inglês
        r"(?i)^abbreviat",
        r"(?i)^abbr(\.|s)?(\s|$)",
        r"(?i)^acronym",
        r"(?i)^list\s+of\s+abbreviat",
        # Português
        r"(?i)^abrevia(ção|ções)",
        r"(?i)^lista\s+de\s+abrevia",
        r"(?i)^siglas?(\s|$)",
        r"(?i)^acrônimos?",
        # Espanhol
        r"(?i)^abrevia(ción|ciones|tura)",
        r"(?i)^lista\s+de\s+abrevia",
        r"(?i)^siglas?(\s|$)",
        r"(?i)^acrónimos?",
        # Francês
        r"(?i)^abréviat",
        r"(?i)^liste\s+d[''e]\s*abréviat",
        r"(?i)^sigles?(\s|$)",
        r"(?i)^acronymes?",
        # Alemão
        r"(?i)^abkürzung",
        r"(?i)^abk(\.|ürzung)",
        r"(?i)^akronyme?",
        r"(?i)^verzeichnis\s+der\s+abkürzung",
        # Africâner
        r"(?i)^afkorting",
        r"(?i)^lys\s+van\s+afkorting",
        r"(?i)^akroniem",
    ],
    "com": [
        # Inglês
        r"(?i)^communicat",
        r"(?i)^communicated\s+by",
        r"(?i)^submitted\s+by",
        r"(?i)^sent\s+by",
        # Português
        r"(?i)^comunicad[oa]\s+(por|pelo|pela)",
        r"(?i)^submetid[oa]\s+(por|pelo|pela)",
        r"(?i)^enviad[oa]\s+(por|pelo|pela)",
        # Espanhol
        r"(?i)^comunicad[oa]\s+por",
        r"(?i)^sometid[oa]\s+por",
        r"(?i)^enviad[oa]\s+por",
        # Francês
        r"(?i)^communiqué\s+par",
        r"(?i)^soumis\s+par",
        r"(?i)^envoyé\s+par",
        # Alemão
        r"(?i)^mitgeteilt\s+(von|durch)",
        r"(?i)^eingereicht\s+(von|durch)",
        r"(?i)^übermittelt\s+(von|durch)",
    ],
    "con": [
        # Inglês
        r"(?i)^contribut",
        r"(?i)^contributed\s+by",
        r"(?i)^contribution",
        r"(?i)^author\s+contribut",
        # Português
        r"(?i)^contribui(ção|ções)",
        r"(?i)^contribuíd[oa]\s+(por|pelo|pela)",
        r"(?i)^contribui(ção|ções)\s+d[oa]s?\s+autor",
        # Espanhol
        r"(?i)^contribu(ción|ciones)",
        r"(?i)^contribuid[oa]\s+por",
        r"(?i)^contribu(ción|ciones)\s+de(l)?\s+autor",
        # Francês
        r"(?i)^contribution",
        r"(?i)^contribué\s+par",
        r"(?i)^contribution\s+de(s)?\s+auteur",
        # Alemão
        r"(?i)^beitrag",
        r"(?i)^beigetragen\s+(von|durch)",
        r"(?i)^autorenbeitrag",
    ],
    "coi-statement": [
        # Inglês
        r"(?i)^conflict.*interest",
        r"(?i)^declaration.*conflict",
        r"(?i)^competing\s+interest",
        r"(?i)^disclosure.*interest",
        r"(?i)^coi(\s|$)",
        # Português
        r"(?i)^conflito.*interesse",
        r"(?i)^declara(ção|ções).*conflito",
        r"(?i)^interesse.*conflitante",
        r"(?i)^divulga(ção|ções).*interesse",
        # Espanhol
        r"(?i)^conflicto.*inter[eé]s",
        r"(?i)^declara(ción|ciones).*conflicto",
        r"(?i)^inter[eé]s.*competitivo",
        r"(?i)^divulga(ción|ciones).*inter[eé]s",
        # Francês
        r"(?i)^conflit.*int[eé]r[eê]t",
        r"(?i)^d[eé]claration.*conflit",
        r"(?i)^int[eé]r[eê]t.*concurrent",
        r"(?i)^divulgation.*int[eé]r[eê]t",
        # Alemão
        r"(?i)^interessenkonflikt",
        r"(?i)^konflikt.*interesse",
        r"(?i)^erkl[aä]rung.*interessenkonflikt",
        r"(?i)^offenlegung.*interesse",
    ],
    "conflict": [
        # Termo mais antigo, mantido por compatibilidade
        r"(?i)^conflict(\s|$)",
        r"(?i)^no\s+conflict",
    ],
    "corresp": [
        # Inglês
        r"(?i)^correspond",
        r"(?i)^corresponding\s+author",
        r"(?i)^address.*correspond",
        r"(?i)^\*correspond",
        r"(?i)^author.*correspond",
        # Português
        r"(?i)^correspond[eê]nc",
        r"(?i)^autor.*correspond",
        r"(?i)^endere[cç]o.*correspond",
        r"(?i)^\*correspond",
        # Espanhol
        r"(?i)^correspond",
        r"(?i)^autor.*correspond",
        r"(?i)^direcci[oó]n.*correspond",
        # Francês
        r"(?i)^correspond",
        r"(?i)^auteur.*correspond",
        r"(?i)^adresse.*correspond",
        # Alemão
        r"(?i)^korrespond",
        r"(?i)^autor.*korrespond",
        r"(?i)^anschrift.*korrespond",
    ],
    "current-aff": [
        # Inglês
        r"(?i)^current\s+(affiliation|address|position)",
        r"(?i)^present\s+(affiliation|address|position)",
        r"(?i)^now\s+at",
        # Português
        r"(?i)^afilia(ção|ções).*atual",
        r"(?i)^endere[cç]o.*atual",
        r"(?i)^posi(ção|ções).*atual",
        r"(?i)^atualmente\s+(em|na|no)",
        # Espanhol
        r"(?i)^afilia(ción|ciones).*actual",
        r"(?i)^direcci[oó]n.*actual",
        r"(?i)^posi(ción|ciones).*actual",
        r"(?i)^actualmente\s+en",
        # Francês
        r"(?i)^affiliation.*actuel",
        r"(?i)^adresse.*actuel",
        r"(?i)^position.*actuel",
        r"(?i)^actuellement",
        # Alemão
        r"(?i)^aktuelle.*zugehörigkeit",
        r"(?i)^derzeitige.*adresse",
        r"(?i)^gegenw[aä]rtige.*position",
        r"(?i)^derzeit\s+bei",
    ],
    "deceased": [
        # Inglês
        r"(?i)^deceased",
        r"(?i)^died",
        r"(?i)^in\s+memoriam",
        r"(?i)^passed\s+away",
        r"(?i)^†",  # Símbolo de cruz
        # Português
        r"(?i)^falecid[oa]",
        r"(?i)^in\s+memoriam",
        r"(?i)^†",
        # Espanhol
        r"(?i)^fallecid[oa]",
        r"(?i)^difunt[oa]",
        r"(?i)^in\s+memoriam",
        # Francês
        r"(?i)^d[eé]c[eé]d[eé]",
        r"(?i)^in\s+memoriam",
        # Alemão
        r"(?i)^verstorben",
        r"(?i)^in\s+memoriam",
    ],
    "edited-by": [
        # Inglês
        r"(?i)^edited\s+by",
        r"(?i)^editor",
        r"(?i)^academic\s+editor",
        r"(?i)^handling\s+editor",
        # Português
        r"(?i)^editad[oa]\s+(por|pelo|pela)",
        r"(?i)^editor",
        r"(?i)^editor.*acad[eê]mic",
        # Espanhol
        r"(?i)^editad[oa]\s+por",
        r"(?i)^editor",
        r"(?i)^editor.*acad[eé]mic",
        # Francês
        r"(?i)^[eé]dit[eé]\s+par",
        r"(?i)^[eé]diteur",
        r"(?i)^r[eé]dacteur",
        # Alemão
        r"(?i)^herausgegeben\s+von",
        r"(?i)^herausgeber",
        r"(?i)^bearbeitet\s+von",
    ],
    "equal": [
        # Inglês
        r"(?i)^equal.*contribut",
        r"(?i)^contributed\s+equally",
        r"(?i)^joint\s+first\s+author",
        r"(?i)^co-first\s+author",
        r"(?i)^\*equal",
        r"(?i)^†equal",
        r"(?i)^‡equal",
        # Português
        r"(?i)^contribui.*igual",
        r"(?i)^contribuíram\s+igualmente",
        r"(?i)^co-primeir[oa]\s+autor",
        r"(?i)^primeir[oa]s?\s+autor.*conjunt",
        # Espanhol
        r"(?i)^contribu.*igual",
        r"(?i)^contribuyeron\s+igualmente",
        r"(?i)^co-primer\s+autor",
        r"(?i)^primer.*autor.*conjunt",
        # Francês
        r"(?i)^contribu.*[eé]gal",
        r"(?i)^contribu[eé]\s+[eé]galement",
        r"(?i)^co-premier\s+auteur",
        # Alemão
        r"(?i)^gleich.*beitrag",
        r"(?i)^gleichberechtigte.*autor",
        r"(?i)^geteilte.*erstautor",
    ],
    "financial-disclosure": [
        # Inglês
        r"(?i)^financial.*disclos",
        r"(?i)^funding",
        r"(?i)^financial\s+support",
        r"(?i)^grant",
        r"(?i)^supported\s+by",
        r"(?i)^financ.*statement",
        # Português
        r"(?i)^divulga.*financ",
        r"(?i)^financiamento",
        r"(?i)^apoio\s+financeiro",
        r"(?i)^aux[ií]lio",
        r"(?i)^apoiad[oa]\s+(por|pelo|pela)",
        r"(?i)^declara.*financ",
        # Espanhol
        r"(?i)^divulga.*financ",
        r"(?i)^financiamiento",
        r"(?i)^financiaci[oó]n",
        r"(?i)^apoyo\s+financiero",
        r"(?i)^subvenci[oó]n",
        r"(?i)^apoyad[oa]\s+por",
        # Francês
        r"(?i)^divulgation.*financ",
        r"(?i)^financement",
        r"(?i)^soutien\s+financier",
        r"(?i)^subvention",
        r"(?i)^soutenu\s+par",
        # Alemão
        r"(?i)^finanz.*offenlegung",
        r"(?i)^finanzierung",
        r"(?i)^f[oö]rderung",
        r"(?i)^unterst[uü]tzt\s+(von|durch)",
    ],
    "on-leave": [
        # Inglês
        r"(?i)^on\s+leave",
        r"(?i)^sabbatical",
        r"(?i)^leave\s+of\s+absence",
        # Português
        r"(?i)^em\s+licen[cç]a",
        r"(?i)^licen[cç]a",
        r"(?i)^sab[aá]tico",
        r"(?i)^afastamento",
        # Espanhol
        r"(?i)^en\s+licencia",
        r"(?i)^licencia",
        r"(?i)^sab[aá]tico",
        r"(?i)^permiso",
        # Francês
        r"(?i)^en\s+cong[eé]",
        r"(?i)^cong[eé]\s+sabbatique",
        # Alemão
        r"(?i)^beurlaubt",
        r"(?i)^sabbatical",
        r"(?i)^freistellung",
    ],
    "participating-researchers": [
        # Inglês
        r"(?i)^participating\s+researcher",
        r"(?i)^research\s+participant",
        r"(?i)^collaborat",
        r"(?i)^research\s+team",
        r"(?i)^study\s+team",
        # Português
        r"(?i)^pesquisador.*participante",
        r"(?i)^participante.*pesquisa",
        r"(?i)^colaborador",
        r"(?i)^equipe.*pesquisa",
        r"(?i)^equipe.*estudo",
        # Espanhol
        r"(?i)^investigador.*participante",
        r"(?i)^participante.*investiga",
        r"(?i)^colaborador",
        r"(?i)^equipo.*investiga",
        # Francês
        r"(?i)^chercheur.*participant",
        r"(?i)^participant.*recherche",
        r"(?i)^collaborateur",
        r"(?i)^[eé]quipe.*recherche",
        # Alemão
        r"(?i)^teilnehmende.*forscher",
        r"(?i)^forschungsteilnehmer",
        r"(?i)^mitarbeiter",
        r"(?i)^forschungsteam",
    ],
    "present-address": [
        # Inglês
        r"(?i)^present\s+address",
        r"(?i)^current\s+address",
        r"(?i)^now\s+at",
        # Português
        r"(?i)^endere[cç]o\s+atual",
        r"(?i)^atualmente\s+em",
        # Espanhol
        r"(?i)^direcci[oó]n\s+actual",
        r"(?i)^actualmente\s+en",
        # Francês
        r"(?i)^adresse\s+actuelle",
        r"(?i)^actuellement",
        # Alemão
        r"(?i)^aktuelle\s+adresse",
        r"(?i)^gegenw[aä]rtige\s+adresse",
        r"(?i)^jetzt\s+bei",
    ],
    "presented-at": [
        # Inglês
        r"(?i)^presented\s+(at|to)",
        r"(?i)^presentation",
        r"(?i)^conference\s+presentation",
        r"(?i)^delivered\s+at",
        # Português
        r"(?i)^apresentad[oa]\s+(em|no|na)",
        r"(?i)^apresenta[cç][aã]o",
        r"(?i)^apresenta[cç][aã]o.*confer[eê]ncia",
        # Espanhol
        r"(?i)^presentad[oa]\s+en",
        r"(?i)^presentaci[oó]n",
        r"(?i)^presentaci[oó]n.*conferencia",
        # Francês
        r"(?i)^pr[eé]sent[eé]\s+[aà]",
        r"(?i)^pr[eé]sentation",
        r"(?i)^pr[eé]sent[eé]\s+lors",
        # Alemão
        r"(?i)^pr[aä]sentiert\s+(bei|auf)",
        r"(?i)^pr[aä]sentation",
        r"(?i)^vorgestellt\s+(bei|auf)",
    ],
    "presented-by": [
        # Inglês
        r"(?i)^presented\s+by",
        r"(?i)^presenter",
        r"(?i)^speaker",
        # Português
        r"(?i)^apresentad[oa]\s+(por|pelo|pela)",
        r"(?i)^apresentador",
        r"(?i)^palestrante",
        # Espanhol
        r"(?i)^presentad[oa]\s+por",
        r"(?i)^presentador",
        r"(?i)^ponente",
        # Francês
        r"(?i)^pr[eé]sent[eé]\s+par",
        r"(?i)^pr[eé]sentateur",
        r"(?i)^conf[eé]rencier",
        # Alemão
        r"(?i)^pr[aä]sentiert\s+(von|durch)",
        r"(?i)^pr[aä]sentator",
        r"(?i)^referent",
    ],
    "previously-at": [
        # Inglês
        r"(?i)^previous",
        r"(?i)^formerly",
        r"(?i)^past\s+(affiliation|address|position)",
        # Português
        r"(?i)^anterior",
        r"(?i)^previamente",
        r"(?i)^afilia[cç][aã]o.*anterior",
        # Espanhol
        r"(?i)^anterior",
        r"(?i)^previamente",
        r"(?i)^afiliaci[oó]n.*anterior",
        # Francês
        r"(?i)^pr[eé]c[eé]demment",
        r"(?i)^ant[eé]rieur",
        r"(?i)^affiliation.*pr[eé]c[eé]dente",
        # Alemão
        r"(?i)^fr[uü]her",
        r"(?i)^vorherige",
        r"(?i)^ehemalige",
    ],
    "study-group-members": [
        # Inglês
        r"(?i)^study\s+group",
        r"(?i)^research\s+group",
        r"(?i)^group\s+member",
        r"(?i)^consortium\s+member",
        r"(?i)^collaborative\s+group",
        # Português
        r"(?i)^grupo\s+de\s+estudo",
        r"(?i)^grupo\s+de\s+pesquisa",
        r"(?i)^membro.*grupo",
        r"(?i)^cons[oó]rcio",
        r"(?i)^grupo\s+colaborativo",
        # Espanhol
        r"(?i)^grupo\s+de\s+estudio",
        r"(?i)^grupo\s+de\s+investigaci[oó]n",
        r"(?i)^miembro.*grupo",
        r"(?i)^consorcio",
        # Francês
        r"(?i)^groupe\s+d'[eé]tude",
        r"(?i)^groupe\s+de\s+recherche",
        r"(?i)^membre.*groupe",
        r"(?i)^consortium",
        # Alemão
        r"(?i)^studiengruppe",
        r"(?i)^forschungsgruppe",
        r"(?i)^gruppenmitglied",
        r"(?i)^konsortium",
    ],
    "supplementary-material": [
        # Inglês
        r"(?i)^supplement",
        r"(?i)^additional\s+(material|information|data|file)",
        r"(?i)^supporting\s+(material|information|data|file)",
        r"(?i)^online\s+supplement",
        r"(?i)^electronic\s+supplement",
        # Português
        r"(?i)^suplementar",
        r"(?i)^material.*adicional",
        r"(?i)^informa[cç].*adicional",
        r"(?i)^dados.*adicionais",
        r"(?i)^arquivo.*suplementar",
        r"(?i)^suplemento.*online",
        # Espanhol
        r"(?i)^suplementario",
        r"(?i)^material.*adicional",
        r"(?i)^informaci[oó]n.*adicional",
        r"(?i)^datos.*adicionales",
        r"(?i)^archivo.*suplementario",
        r"(?i)^suplemento.*en\s+l[ií]nea",
        # Francês
        r"(?i)^suppl[eé]mentaire",
        r"(?i)^mat[eé]riel.*additionnel",
        r"(?i)^information.*suppl[eé]mentaire",
        r"(?i)^donn[eé]es.*suppl[eé]mentaires",
        r"(?i)^fichier.*suppl[eé]mentaire",
        # Alemão
        r"(?i)^erg[aä]nzend",
        r"(?i)^zusatzmaterial",
        r"(?i)^zus[aä]tzliche.*information",
        r"(?i)^erg[aä]nzungsmaterial",
        r"(?i)^online.*erg[aä]nzung",
    ],
    "supported-by": [
        # Inglês
        r"(?i)^support",
        r"(?i)^sponsored",
        r"(?i)^funded\s+by",
        r"(?i)^grant.*support",
        # Português
        r"(?i)^apoia",
        r"(?i)^patrocina",
        r"(?i)^financiad[oa]\s+(por|pelo|pela)",
        r"(?i)^suporte.*financeiro",
        # Espanhol
        r"(?i)^apoya",
        r"(?i)^patrocina",
        r"(?i)^financiad[oa]\s+por",
        r"(?i)^apoyo.*financiero",
        # Francês
        r"(?i)^soutenu",
        r"(?i)^parrain[eé]",
        r"(?i)^financ[eé]\s+par",
        r"(?i)^soutien.*financier",
        # Alemão
        r"(?i)^unterst[uü]tzt",
        r"(?i)^gef[oö]rdert",
        r"(?i)^gesponsert",
        r"(?i)^finanziert\s+(von|durch)",
    ],
}

# Mapeamento de símbolos especiais que podem indicar tipos específicos de footnotes
SYMBOL_TO_FN_TYPE = {
    "*": "corresp",  # Asterisco geralmente para correspondência
    "†": "deceased",  # Cruz para falecido ou contribuição igual
    "‡": "equal",  # Double dagger para contribuição igual
    "§": "present-address",  # Section sign para endereço atual
    "¶": "other",  # Pilcrow para outras notas
    "#": "equal",  # Hash para contribuição igual
    "**": "equal",  # Double asterisk para contribuição igual
    "††": "equal",  # Double dagger para contribuição igual
}

# Padrões para detecção de números de nota de rodapé
FN_NUMBER_PATTERNS = [
    r"^(\d+)\.?\s*",  # 1. ou 1
    r"^\[(\d+)\]",  # [1]
    r"^\((\d+)\)",  # (1)
    r"^([a-z])\.?\s*",  # a. ou a
    r"^\[([a-z])\]",  # [a]
    r"^\(([a-z])\)",  # (a)
    r"^([A-Z])\.?\s*",  # A. ou A
    r"^\[([A-Z])\]",  # [A]
    r"^\(([A-Z])\)",  # (A)
    r"^([*†‡§¶#]+)\s*",  # Símbolos especiais
    r"^(\d+[a-z]?)\.?\s*",  # 1a. ou 1a
]

# Lista de termos que indicam definitivamente que NÃO é uma footnote
NOT_FN_INDICATORS = [
    # Termos de seções já cobertos por SEC_TYPE_PATTERNS
    r"(?i)^(introduction|methods?|results?|discussion|conclusion)",
    r"(?i)^(introdu[cç][aã]o|m[eé]todos?|resultados?|discuss[aã]o|conclus)",
    r"(?i)^(introducci[oó]n|m[eé]todos?|resultados?|discusi[oó]n|conclus)",
    # Termos estruturais
    r"(?i)^(abstract|summary|keywords|resumen|resumo)",
    r"(?i)^(background|objective|materials?|procedures?)",
    r"(?i)^(acknowledge?ments?|agradecimentos?|references?|refer[eê]ncias?)",
    # Numeração de seções
    r"^\d+\.\d+",  # 2.1, 3.2, etc.
    r"^[IVX]+\.",  # I., II., III. (números romanos para seções)
    r"^Chapter\s+\d",  # Chapter 1
    r"^Part\s+[IVX]",  # Part I
]
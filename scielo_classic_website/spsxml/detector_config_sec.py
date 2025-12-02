# Padrões para detecção de sec-type em múltiplos idiomas
SEC_TYPE_PATTERNS = {
    "cases": [
        # Inglês
        r"(?i)^cases?(\s+stud(y|ies))?",
        r"(?i)^case\s+report",
        r"(?i)^case\s+stud(y|ies)",
        r"(?i)^clinical\s+cases?",
        # Português
        r"(?i)^relatos?(\s+de\s+casos?)?",
        r"(?i)^casos?(\s+clínicos?)?",
        r"(?i)^estudos?\s+de\s+casos?",
        # Espanhol
        r"(?i)^casos?(\s+clínicos?)?",
        r"(?i)^informes?\s+de\s+casos?",
        r"(?i)^estudios?\s+de\s+casos?",
        r"(?i)^reporte\s+de\s+casos?",
        # Francês
        r"(?i)^cas(\s+cliniques?)?",
        r"(?i)^études?\s+de\s+cas",
        r"(?i)^rapport\s+de\s+cas",
        r"(?i)^présentation\s+de\s+cas",
        # Alemão
        r"(?i)^fälle?",
        r"(?i)^fallbericht",
        r"(?i)^fallstudien?",
        r"(?i)^kasuistik",
        # Africâner
        r"(?i)^gevalle?",
        r"(?i)^gevallestudies?",
        r"(?i)^kliniese\s+gevalle?",
    ],
    "conclusions": [
        # Inglês
        r"(?i)^conclusions?",
        r"(?i)^concluding\s+remarks?",
        r"(?i)^final\s+(remarks?|comments?|considerations?)",
        r"(?i)^summary",
        # Português
        r"(?i)^conclus(ão|ões)",
        r"(?i)^considera(ção|ções)\s+fina(l|is)",
        r"(?i)^comentários?\s+fina(l|is)",
        r"(?i)^resumo\s+final",
        # Espanhol
        r"(?i)^conclusiones?",
        r"(?i)^consideraciones?\s+finales?",
        r"(?i)^comentarios?\s+finales?",
        r"(?i)^observaciones?\s+finales?",
        # Francês
        r"(?i)^conclusions?",
        r"(?i)^remarques?\s+finales?",
        r"(?i)^considérations?\s+finales?",
        r"(?i)^commentaires?\s+finaux?",
        # Alemão
        r"(?i)^schlussfolgerung(en)?",
        r"(?i)^fazit",
        r"(?i)^zusammenfassung",
        r"(?i)^schlussbemerkung(en)?",
        r"(?i)^abschließende\s+bemerkung(en)?",
        # Africâner
        r"(?i)^gevolgtrekking(s)?",
        r"(?i)^slotsom",
        r"(?i)^finale\s+opmerkings?",
        r"(?i)^slotopmerkings?",
    ],
    "data-availability": [
        # Inglês
        r"(?i)^data\s+availability",
        r"(?i)^availability\s+of\s+data",
        r"(?i)^data\s+sharing",
        r"(?i)^data\s+accessibility",
        r"(?i)^data\s+statement",
        # Português
        r"(?i)^disponibilidade\s+de\s+dados",
        r"(?i)^declara(ção|ções)\s+de\s+disponibilidade\s+de\s+dados",
        r"(?i)^compartilhamento\s+de\s+dados",
        r"(?i)^acesso\s+aos?\s+dados",
        # Espanhol
        r"(?i)^disponibilidad\s+de(\s+los)?\s+datos",
        r"(?i)^declaración\s+de\s+disponibilidad\s+de\s+datos",
        r"(?i)^compartición\s+de\s+datos",
        r"(?i)^acceso\s+a\s+los\s+datos",
        # Francês
        r"(?i)^disponibilité\s+des?\s+données",
        r"(?i)^déclaration\s+de\s+disponibilité\s+des?\s+données",
        r"(?i)^partage\s+de(s)?\s+données",
        r"(?i)^accès\s+aux?\s+données",
        # Alemão
        r"(?i)^datenverfügbarkeit",
        r"(?i)^verfügbarkeit\s+der\s+daten",
        r"(?i)^datenfreigabe",
        r"(?i)^datenzugang",
        # Africâner
        r"(?i)^databeskikbaarheid",
        r"(?i)^beskikbaarheid\s+van\s+data",
        r"(?i)^data\s+deel",
        r"(?i)^datatoegang",
    ],
    "discussion": [
        # Inglês
        r"(?i)^discussions?",
        r"(?i)^interpretations?",
        # Português
        r"(?i)^discuss(ão|ões)",
        r"(?i)^interpreta(ção|ções)",
        # Espanhol
        r"(?i)^discusi(ón|ones)",
        r"(?i)^interpretaci(ón|ones)",
        # Francês
        r"(?i)^discussions?",
        r"(?i)^interprétations?",
        # Alemão
        r"(?i)^diskussion(en)?",
        r"(?i)^besprechung(en)?",
        r"(?i)^interpretation(en)?",
        r"(?i)^erörterung(en)?",
        # Africâner
        r"(?i)^bespreking(s)?",
        r"(?i)^diskussie(s)?",
        r"(?i)^interpretasie(s)?",
    ],
    "intro": [
        # Inglês
        r"(?i)^introduction",
        r"(?i)^intro",
        r"(?i)^synopsis",
        r"(?i)^background",
        r"(?i)^overview",
        # Português
        r"(?i)^introdu(ção|ções)",
        r"(?i)^sinopse",
        r"(?i)^contextualiza(ção|ções)",
        r"(?i)^apresenta(ção|ções)",
        # Espanhol
        r"(?i)^introducci(ón|ones)",
        r"(?i)^sinopsis",
        r"(?i)^antecedentes",
        r"(?i)^presentaci(ón|ones)",
        # Francês
        r"(?i)^introduction",
        r"(?i)^synopsis",
        r"(?i)^contexte",
        r"(?i)^présentation",
        r"(?i)^aperçu",
        # Alemão
        r"(?i)^einleitung",
        r"(?i)^einführung",
        r"(?i)^überblick",
        r"(?i)^hintergrund",
        r"(?i)^vorstellung",
        # Africâner
        r"(?i)^inleiding",
        r"(?i)^agtergrond",
        r"(?i)^oorsig",
        r"(?i)^sinopsis",
    ],
    "materials": [
        # Inglês
        r"(?i)^materials?(\s+and\s+methods?)?",
        r"(?i)^materials?\s+used",
        # Português
        r"(?i)^materia(l|is)(\s+e\s+métodos?)?",
        r"(?i)^materia(l|is)\s+utilizado",
        # Espanhol
        r"(?i)^materiales?(\s+y\s+métodos?)?",
        r"(?i)^materiales?\s+utilizados?",
        # Francês
        r"(?i)^matériels?(\s+et\s+méthodes?)?",
        r"(?i)^matériaux",
        # Alemão
        r"(?i)^material(ien)?(\s+und\s+methoden)?",
        r"(?i)^werkstoffe",
        # Africâner
        r"(?i)^materiaal(\s+en\s+metodes)?",
        r"(?i)^materiale",
    ],
    "methods": [
        # Inglês
        r"(?i)^methods?",
        r"(?i)^methodology",
        r"(?i)^methodologies",
        r"(?i)^procedures?",
        r"(?i)^experimental\s+(design|procedures?|methods?)",
        r"(?i)^materials?\s+and\s+methods?",
        # Português
        r"(?i)^métodos?",
        r"(?i)^metodologia(s)?",
        r"(?i)^procedimentos?",
        r"(?i)^materia(l|is)\s+e\s+métodos?",
        r"(?i)^delineamento\s+experimental",
        # Espanhol
        r"(?i)^métodos?",
        r"(?i)^metodología(s)?",
        r"(?i)^procedimientos?",
        r"(?i)^materiales?\s+y\s+métodos?",
        r"(?i)^diseño\s+experimental",
        # Francês
        r"(?i)^méthodes?",
        r"(?i)^méthodologie(s)?",
        r"(?i)^procédures?",
        r"(?i)^matériels?\s+et\s+méthodes?",
        r"(?i)^protocole\s+expérimental",
        # Alemão
        r"(?i)^methode(n)?",
        r"(?i)^methodik",
        r"(?i)^verfahren",
        r"(?i)^material(ien)?\s+und\s+methoden",
        r"(?i)^versuchsaufbau",
        # Africâner
        r"(?i)^metodes?",
        r"(?i)^metodologie",
        r"(?i)^prosedures?",
        r"(?i)^materiaal\s+en\s+metodes",
    ],
    "results": [
        # Inglês
        r"(?i)^results?",
        r"(?i)^findings?",
        r"(?i)^outcomes?",
        # Português
        r"(?i)^resultados?",
        r"(?i)^descobertas?",
        r"(?i)^achados?",
        # Espanhol
        r"(?i)^resultados?",
        r"(?i)^hallazgos?",
        r"(?i)^descubrimientos?",
        # Francês
        r"(?i)^résultats?",
        r"(?i)^découvertes?",
        r"(?i)^constatations?",
        # Alemão
        r"(?i)^ergebnisse?",
        r"(?i)^resultate?",
        r"(?i)^befunde?",
        r"(?i)^erkenntnisse?",
        # Africâner
        r"(?i)^resultate?",
        r"(?i)^uitslae?",
        r"(?i)^bevindinge?",
    ],
    "subjects": [
        # Inglês
        r"(?i)^subjects?",
        r"(?i)^participants?",
        r"(?i)^patients?",
        r"(?i)^study\s+population",
        r"(?i)^sample",
        # Português
        r"(?i)^participantes?",
        r"(?i)^pacientes?",
        r"(?i)^sujeitos?",
        r"(?i)^popula(ção|ções)\s+do\s+estudo",
        r"(?i)^amostra(gem)?",
        r"(?i)^casuística",
        # Espanhol
        r"(?i)^participantes?",
        r"(?i)^pacientes?",
        r"(?i)^sujetos?",
        r"(?i)^poblaci(ón|ones)\s+de(l)?\s+estudio",
        r"(?i)^muestra",
        # Francês
        r"(?i)^participants?",
        r"(?i)^patients?",
        r"(?i)^sujets?",
        r"(?i)^population\s+d'étude",
        r"(?i)^échantillon",
        # Alemão
        r"(?i)^teilnehmer",
        r"(?i)^patienten",
        r"(?i)^probanden",
        r"(?i)^studienpopulation",
        r"(?i)^stichprobe",
        # Africâner
        r"(?i)^deelnemers?",
        r"(?i)^pasiënte?",
        r"(?i)^proefpersone?",
        r"(?i)^studiepopulasie",
        r"(?i)^steekproef",
    ],
    "supplementary-material": [
        # Inglês
        r"(?i)^supplementar(y|ial)\s+material",
        r"(?i)^additional\s+material",
        r"(?i)^supporting\s+information",
        r"(?i)^appendix",
        r"(?i)^appendices",
        # Português
        r"(?i)^material\s+suplementar",
        r"(?i)^material\s+adicional",
        r"(?i)^informa(ção|ções)\s+suplementar(es)?",
        r"(?i)^apêndice",
        # Espanhol
        r"(?i)^material\s+suplementario",
        r"(?i)^material\s+adicional",
        r"(?i)^informaci(ón|ones)\s+suplementaria",
        r"(?i)^apéndice",
        # Francês
        r"(?i)^matériel\s+supplémentaire",
        r"(?i)^matériel\s+additionnel",
        r"(?i)^informations?\s+supplémentaires?",
        r"(?i)^appendice",
        # Alemão
        r"(?i)^ergänzendes?\s+material",
        r"(?i)^zusätzliches?\s+material",
        r"(?i)^supplementäres?\s+material",
        r"(?i)^anhang",
        # Africâner
        r"(?i)^aanvullende\s+materiaal",
        r"(?i)^bykomende\s+materiaal",
        r"(?i)^bylaag",
    ],
    "transcript": [
        # Inglês
        r"(?i)^transcript(ion)?",
        r"(?i)^video\s+transcript(ion)?",
        r"(?i)^audio\s+transcript(ion)?",
        # Português
        r"(?i)^transcri(ção|ções)",
        r"(?i)^transcri(ção|ções)\s+de\s+v[íi]deo",
        r"(?i)^transcri(ção|ções)\s+de\s+[áa]udio",
        # Espanhol
        r"(?i)^transcripci(ón|ones)",
        r"(?i)^transcripci(ón|ones)\s+de(l)?\s+v[íi]deo",
        r"(?i)^transcripci(ón|ones)\s+de(l)?\s+audio",
        # Francês
        r"(?i)^transcription",
        r"(?i)^transcription\s+vidéo",
        r"(?i)^transcription\s+audio",
        # Alemão
        r"(?i)^transkript(ion)?",
        r"(?i)^videotranskript(ion)?",
        r"(?i)^audiotranskript(ion)?",
        r"(?i)^niederschrift",
        # Africâner
        r"(?i)^transkripsie",
        r"(?i)^video\s+transkripsie",
        r"(?i)^oudio\s+transkripsie",
    ],
}

COMBINED_PATTERNS = [
    # Materials/Methods combinados
    (r"materia(l|is|ls)?\s+(and|&|e|y|et|und|en)\s+m[eé]t[oóh]od", ["materials", "methods"]),
    (r"m[eé]t[oóh]odos?\s+(and|&|e|y|et|und|en)\s+materia", ["methods", "materials"]),
    (r"matériels?\s+et\s+méthodes?", ["materials", "methods"]),
    (r"materiales?\s+y\s+métodos?", ["materials", "methods"]),
    (r"material(ien)?\s+und\s+methoden", ["materials", "methods"]),
    (r"materiaal\s+en\s+metodes", ["materials", "methods"]),
    
    # Results/Discussion combinados
    (r"results?\s+(and|&|e|y|et|und|en)\s+discuss", ["results", "discussion"]),
    (r"resultados?\s+(e|y)\s+discuss", ["results", "discussion"]),
    (r"résultats?\s+et\s+discussion", ["results", "discussion"]),
    (r"ergebnisse?\s+und\s+diskussion", ["results", "discussion"]),
    (r"resultate?\s+en\s+bespreking", ["results", "discussion"]),
    
    # Discussion/Results (ordem inversa)
    (r"discuss(ão|ões|ion|ión)?\s+(and|&|e|y|et|und|en)\s+results?", ["discussion", "results"]),
    
    # Conclusions combinadas
    (r"conclus(ions?|ões?|iones?)?\s+(and|&|e|y|et|und|en)\s+(future|perspectives?|recommendations?)", 
        ["conclusions"]),
    (r"conclus(ions?|ões?|iones?)?\s+(and|&|e|y|et|und|en)\s+(final\s+)?(remarks?|comments?|considerations?)", 
        ["conclusions"]),
    
    # Subjects/Methods combinados
    (r"(participants?|patients?|subjects?)\s+(and|&|e|y|et|und|en)\s+methods?", ["subjects", "methods"]),
    (r"(participantes?|pacientes?)\s+(e|y)\s+métodos?", ["subjects", "methods"]),
    
    # Cases/Results combinados
    (r"cases?\s+(and|&|e|y|et|und|en)\s+results?", ["cases", "results"]),
    (r"casos?\s+(e|y)\s+resultados?", ["cases", "results"]),
]

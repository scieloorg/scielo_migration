from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.front_text import (
    FrontMetadata,
    strip_front_text,
    strip_trailing_front_text,
)
from scielo_classic_website.spsxml.sps_xml_body_pipes import XMLStripFrontTextPipe

TITLE = "Tratamiento médico en pacientes con infestación por Angiostrongylus costaricensis"
TRANS_TITLE = "Medical treatment in patients with Angiostrongylus costaricensis infestation"
ABSTRACT = (
    "Se presentan dos casos de infestación por Angiostrongylus costaricensis; uno grave, "
    "que requirió resección quirúrgica y dos cursos de tratamiento con albendazol para su "
    "resolución exitosa, y otro en el que el tratamiento temprano permitió al paciente "
    "curarse sin complicaciones."
)
TRANS_ABSTRACT = (
    "These are two cases of Angiostrongylus costaricensis infestation. In case one surgical "
    "treatment was required together with two courses of albendazole, and in case two the "
    "early treatment allowed the patient to recover without complications."
)
INTRO = (
    "Paciente masculino de 23 años de edad con una semana de evolución de fiebre alta. Fue "
    "visto por un médico y tratado con claritromicina, sin resultado en los primeros tres días."
)
DISCUSSION = (
    "La angiostrongilosis abdominal es una zoonosis endémica en Costa Rica, cuyo diagnóstico "
    "temprano depende de la sospecha clínica y de los hallazgos de laboratorio."
)


class HRecord:
    article_titles = [
        {"text": TITLE, "language": "es"},
        {"text": TRANS_TITLE, "language": "en"},
    ]
    abstracts = [
        {"text": ABSTRACT, "language": "es"},
        {"text": TRANS_ABSTRACT, "language": "en"},
    ]
    keywords = [
        {"text": "angiostrongilosis", "language": "es"},
        {"text": "albendazol", "language": "es"},
    ]
    authors = [
        {"given_names": "Verny", "surname": "Huertas-Franco"},
        {"given_names": "Álvaro", "surname": "Camacho-Fernández"},
    ]
    corporative_authors = []
    affiliations = [{"id": "a1", "orgname": "Hospital San Juan de Dios, Caja Costarricense de Seguro Social"}]


class Document:
    def __init__(self, h_record=HRecord()):
        self.h_record = h_record

    def get_sections(self):
        return {"es": {"text": "Caso clínico"}, "en": {"text": "Clinical case"}}


def body(content):
    return etree.fromstring(f"<body>{content}</body>")


def texts(node):
    return [" ".join(" ".join(n.itertext()).split()) for n in node]


FRONT = (
    "<p>Caso clínico</p>"
    f'<p align="center">{TITLE}</p>'
    "<p>Verny Huertas- Franco, Álvaro Camacho- Fernández.</p>"
    "<abstract><title>Resumen</title></abstract>"
    f"<p>{ABSTRACT}</p>"
    "<p><bold>Descriptores: </bold>angiostrongilosis, albendazol</p>"
    "<p>Recibido: 21 de junio de 2005 Aceptado: 17 de octubre de 2006</p>"
)


class StripFrontTextTest(TestCase):
    def setUp(self):
        self.metadata = FrontMetadata.from_document(Document())

    def test_front_at_the_start_of_the_body_is_removed(self):
        node = body(FRONT + f'<sec sec-type="cases"><title>Caso clínico #1</title><p>{INTRO}</p></sec>')
        removed = strip_front_text(node, self.metadata)
        self.assertEqual(len(removed), 7)
        self.assertEqual(texts(node), [f"Caso clínico #1 {INTRO}"])

    def test_subheading_equal_to_the_toc_section_stays(self):
        node = body(f"<p>Caso clínico</p><p>{TITLE}</p><p>Caso clínico</p><p>{INTRO}</p>")
        strip_front_text(node, self.metadata)
        self.assertEqual(texts(node), ["Caso clínico", INTRO])

    def test_section_with_front_and_introduction_keeps_the_introduction(self):
        node = body(f"<sec><title>{TITLE}</title><p>Verny Huertas-Franco</p><p>{ABSTRACT}</p><p>{INTRO}</p></sec>")
        strip_front_text(node, self.metadata)
        self.assertEqual(etree.tostring(node, encoding="unicode"), f"<body><sec><p>{INTRO}</p></sec></body>")

    def test_abstract_not_registered_stays_with_its_label(self):
        metadata = FrontMetadata([TITLE], [TITLE], [TITLE])
        node = body(f"<p>{TITLE}</p><p>Resumen</p><p>{INTRO}</p><p>{DISCUSSION}</p>")
        strip_front_text(node, metadata)
        self.assertEqual(texts(node), ["Resumen", INTRO, DISCUSSION])

    def test_keywords_not_registered_stay(self):
        node = body(f"<p>{TITLE}</p><p>Palabras clave: zoonosis, nematodos</p><p>{INTRO}</p>")
        strip_front_text(node, self.metadata)
        self.assertEqual(texts(node), ["Palabras clave: zoonosis, nematodos", INTRO])

    def test_subtitle_that_looks_like_a_label_stays(self):
        node = body(f"<p>{TITLE}</p><p>Resumen del caso</p><p>{INTRO}</p>")
        strip_front_text(node, self.metadata)
        self.assertEqual(texts(node), ["Resumen del caso", INTRO])

    def test_short_subheading_found_inside_the_abstract_stays(self):
        node = body(f"<p>{TITLE}</p><p>Albendazol</p><p>{INTRO}</p>")
        strip_front_text(node, self.metadata)
        self.assertEqual(texts(node), ["Albendazol", INTRO])

    def test_title_broken_in_lines(self):
        node = body(
            "<p>Tratamiento médico en pacientes</p><p>con infestación por</p>"
            f"<p>Angiostrongylus costaricensis</p><p>{INTRO}</p>"
        )
        strip_front_text(node, self.metadata)
        self.assertEqual(texts(node), [INTRO])

    def test_box_that_repeats_the_abstract_stays(self):
        node = body(f"<p>{TITLE}</p><p>{ABSTRACT}</p><p>Cuadro 1 {ABSTRACT}</p><p>{INTRO}</p>")
        strip_front_text(node, self.metadata)
        self.assertEqual(texts(node), [f"Cuadro 1 {ABSTRACT}", INTRO])

    def test_body_is_never_emptied(self):
        node = body(f"<p>{TITLE}</p><p>{ABSTRACT}</p>")
        self.assertEqual(strip_front_text(node, self.metadata), [])
        self.assertEqual(len(node), 2)

    def test_without_metadata_nothing_is_removed(self):
        node = body(FRONT + f"<p>{INTRO}</p>")
        self.assertEqual(strip_front_text(node, FrontMetadata([])), [])


class StripTrailingFrontTextTest(TestCase):
    def setUp(self):
        self.metadata = FrontMetadata.from_document(Document())

    def test_translated_abstract_after_the_discussion_is_removed(self):
        node = body(
            f"<sec><title>Discusión</title><p>{DISCUSSION}</p>"
            f"<p>Abstract</p><p>{TRANS_ABSTRACT}</p><p>Key words: angiostrongilosis, albendazol</p><p/></sec>"
        )
        removed = strip_trailing_front_text(node, self.metadata)
        self.assertEqual(len(removed), 4)
        self.assertEqual(texts(node), [f"Discusión {DISCUSSION}"])

    def test_conclusion_that_repeats_the_abstract_stays(self):
        node = body(f"<p>{INTRO}</p><p>{ABSTRACT}</p>")
        self.assertEqual(strip_trailing_front_text(node, self.metadata), [])
        self.assertEqual(texts(node), [INTRO, ABSTRACT])

    def test_editorial_signature_stays(self):
        node = body(
            f"<p>{DISCUSSION}</p><p>Abstract</p><p>Verny Huertas-Franco</p>"
            "<p>Hospital San Juan de Dios, Caja Costarricense de Seguro Social</p>"
        )
        self.assertEqual(strip_trailing_front_text(node, self.metadata), [])
        self.assertEqual(len(node), 4)


class XMLStripFrontTextPipeTest(TestCase):
    def test_uses_the_document_metadata(self):
        xml = etree.fromstring(
            f"<article><body>{FRONT}<p>{INTRO}</p><p>Abstract</p><p>{TRANS_ABSTRACT}</p></body><back/></article>"
        )
        XMLStripFrontTextPipe().transform((Document(), xml))
        self.assertEqual(texts(xml.find("body")), [INTRO])

    def test_document_without_metadata(self):
        xml = etree.fromstring(f"<article><body>{FRONT}<p>{INTRO}</p></body></article>")
        XMLStripFrontTextPipe().transform((Document(h_record=None), xml))
        self.assertEqual(len(xml.find("body")), 8)

    def test_sec_intro_rule_still_applies(self):
        xml = etree.fromstring(
            "<article><body><p>Texto não cadastrado</p>"
            f'<sec sec-type="intro"><title>Introducción</title><p>{INTRO}</p></sec></body></article>'
        )
        XMLStripFrontTextPipe().transform((Document(h_record=None), xml))
        self.assertEqual(texts(xml.find("body")), [f"Introducción {INTRO}"])

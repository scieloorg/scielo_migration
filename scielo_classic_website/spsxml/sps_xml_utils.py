from lxml import etree as ET

from scielo_classic_website.exceptions import GetSectionTitleException


def set_subject_text(subject_node, document, language):
    try:
        subject_node.text = document.get_section_title(language)
    except GetSectionTitleException as e:
        comment = ET.Comment(str(e))
        subject_node.addnext(comment)
        try:
            subject_node.text = document.get_sections()[0]["text"]
        except (IndexError, KeyError):
            pass

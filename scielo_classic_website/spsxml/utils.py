from lxml import etree


def convert_ahref_to_extlink(xml_etree):
    """
    This methods receives an etree node and replace all "a href" elements to
    a valid ext-link jats compliant format.
    """

    for ahref in xml_etree.findall(".//a"):
        uri = ahref.get("href", "")

        if len(uri) == 0 or not uri.strip().startswith("http"):
            continue

        ahref.tag = "ext-link"
        ahref.set("ext-link-type", "uri")
        ahref.set("{http://www.w3.org/1999/xlink}href", uri)
        for key in ahref.attrib.keys():
            if key not in ["ext-link-type", "{http://www.w3.org/1999/xlink}href"]:
                ahref.attrib.pop(key)

    return xml_etree


def convert_html_tags_to_jats(xml_etree):
    """
    This methods receives an etree node and replace all "html tags" to
    jats compliant tags.
    """

    tags = (("strong", "bold"), ("i", "italic"), ("u", "underline"), ("small", "sc"))

    for from_tag, to_tag in tags:
        for element in xml_etree.findall(".//" + from_tag):
            element.tag = to_tag

    return xml_etree


def convert_all_html_tags_to_jats(xml_etree):
    xml_etree = convert_ahref_to_extlink(xml_etree)
    xml_etree = convert_html_tags_to_jats(xml_etree)

    return xml_etree


def handle_bad_text(node, text):
    try:
        node.text = text
    except Exception as e:
        node.append(etree.Comment(str(e)))
        node.text = handle_bad_characters(text)


def handle_bad_characters(text):
    if not text:
        return None
    chars = []
    temporary = etree.Element("temporary")
    for c in text:
        try:
            temporary.text = c
            chars.append(c)
        except Exception as exc:
            chars.append('?')
    return ''.join(chars)

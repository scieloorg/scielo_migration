"""
Origem: https://github.com/scieloorg/xylose/blob/262126e37e55bb7df2ebc585472f260daddedce9/xylose/scielodocument.py

"""
import logging
import re
import sys
import unicodedata
import warnings

try:  # Keep compatibility with python 2.7
    from html import unescape
except ImportError:
    from HTMLParser import HTMLParser


allowed_formats = ['iso 639-2', 'iso 639-1', None]

# --------------
# Py2 compat
# --------------
PY2 = sys.version_info[0] == 2

if PY2:
    html_parser = HTMLParser().unescape
else:
    html_parser = unescape

_charref = re.compile(r'&(#[0-9]+;?'
                      r'|#[xX][0-9a-fA-F]+;?'
                      r'|[^\t\n\f <&#;]{1,32};?)')


def html_safe_decode(
    string, forbidden=["&lt;", "&gt;", "&amp;", "&#60;", "&#62;", "&#38;"]
):
    """
    >>> html_safe_decode("26. Cohen J. The Earth is Round (p.05&gt;Am Psychol 1994; 49: 997-1003")
    >>> "26. Cohen J. The Earth is Round (p.05&gt;Am Psychol 1994; 49: 997-1003"
    """
    if "&" not in string:
        return string

    def replace_charref(s):
        s = "&" + s.group(1)
        if s in forbidden:
            return s
        return html_parser(s)

    return _charref.sub(replace_charref, string)


# --------------

LICENSE_REGEX = re.compile(r'a.+?href="(.+?)"')
LICENSE_CREATIVE_COMMONS = re.compile(r'licenses/(.*?/\d\.\d)') # Extracts the creative commons id from the url.
DOI_REGEX = re.compile(r'\d{2}\.\d+/.*$')
SUPPLBEG_REGEX = re.compile(r'^0 ')
SUPPLEND_REGEX = re.compile(r' 0$')
CLEANUP_MIXED_CITATION = re.compile(r'< *?p.*?>|< *?f.*?>|< *?tt.*?>|< *?span.*?>|< *?cite.*?>|< *?country-region.*?>|< *?region.*?>|< *?place.*?>|< *?state.*?>|< *?city.*?>|< *?dir.*?>|< *?li.*?>|< *?ol.*?>|< *?dt.*?>|< *?dd.*?>|< *?hr.*?>|< *?/ *?p.*?>|< *?/ *?f.*?>|< *?/ *?tt.*?>|< *?/ *?span.*?>|< *?/ *?cite.*?>|< *?/ *?country-region.*?>|< *?/ *?region.*?>|< *?/ *?place.*?>|< *?/ *?state.*?>|< *?/ *?city.*?>|< *?/ *?dir.*?>|< *?/ *?li.*?>|< *?/ *?ol.*?>|< *?/ *?dt.*?>|< *?/ *?dd.*?>', re.IGNORECASE)
REPLACE_TAGS_MIXED_CITATION = (
    (re.compile(r'< *?i.*?>', re.IGNORECASE), '<i>',),
    (re.compile(r'< *?/ *?i.*?>', re.IGNORECASE), '</i>',),
    (re.compile(r'< *?u.*?>', re.IGNORECASE), '<u>',),
    (re.compile(r'< *?/ *?u.*?>', re.IGNORECASE), '</u>',),
    (re.compile(r'< *?b.*?>', re.IGNORECASE), '<strong>',),
    (re.compile(r'< *?/ *?b.*?>', re.IGNORECASE), '</strong>',),
    (re.compile(r'< *?em.*?>', re.IGNORECASE), '<strong>',),
    (re.compile(r'< *?/ *?em.*?>', re.IGNORECASE), '</strong>',),
    (re.compile(r'< *?small.*?>', re.IGNORECASE), '<small>',),
    (re.compile(r'< *?/ *?small.*?>', re.IGNORECASE), '</small>',),
)
EMAIL_REGEX = re.compile(
    r'(?P<open_anchor>a href)=(?P<href>\".*\")>(?P<email>.*)<(?P<close_anchor>\/a|\/A)',
    re.IGNORECASE
)


def warn_future_deprecation(old, new, details=''):
    msg = '"{}" will be deprecated in future version. '.format(old) + \
        'Use "{}" instead. {}'.format(new, details)
    warnings.warn(msg, PendingDeprecationWarning)


class XyloseException(Exception):
    pass


class UnavailableMetadataException(XyloseException):
    pass


def cleanup_number(text):
    """
    Lefting just valid numbers
    """

    return ''.join([i for i in text if i.isdigit()])


def cleanup_string(text):
    """
    Remove any special character like -,./ lefting just numbers and alphabet
    characters
    """

    try:
        nfd_form = unicodedata.normalize('NFD', text.strip().lower())
    except TypeError:
        nfd_form = unicodedata.normalize('NFD', unicode(text.strip().lower()))

    cleaned_str = u''.join(x for x in nfd_form if unicodedata.category(x)[0] == 'L' or x == ' ')

    return cleaned_str


def remove_control_characters(data):
    return "".join(ch for ch in data if unicodedata.category(ch)[0] != "C")


def html_decode(string):

    try:
        string = html_parser(string)
    except Exception as e:
        logging.exception(f"html_decode({string} {e}")
        return string

    try:
        return remove_control_characters(string)
    except Exception as e:
        logging.exception(f"html_decode({string} {e}")
        return string


def email_html_remove(string):
    result = EMAIL_REGEX.search(string)
    if result is None:
        return string

    try:
        return result.group("email")
    except:
        return string

import os
import glob


from scielo_classic_website import exceptions


ATTRIBUTES_PATH = os.environ.get("ATTRIBUTES_PATH", 'scielo_classic_website/settings/attributes')

# /var/www/scielo/proc/cisis
CLASSIC_WEBSITE_CISIS_PATH = os.environ.get("CLASSIC_WEBSITE_CISIS_PATH")

CLASSIC_WEBSITE_BASES_WORK_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_WORK_PATH")
CLASSIC_WEBSITE_BASES_XML_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_XML_PATH")
CLASSIC_WEBSITE_BASES_PDF_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_PDF_PATH")
CLASSIC_WEBSITE_BASES_TRANSLATION_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_TRANSLATION_PATH")
CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH = os.environ.get("CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH")
CLASSIC_WEBSITE_BASES_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_PATH")


def get_cisis_path():
    """
    Get CLASSIC_WEBSITE_CISIS_PATH
    """
    if not CLASSIC_WEBSITE_CISIS_PATH:
        raise exceptions.MissingCisisPathEnvVarError(
            "Missing value for environment variable CLASSIC_WEBSITE_CISIS_PATH. "
            "CLASSIC_WEBSITE_CISIS_PATH=/var/www/scielo/proc/cisis"
        )
    if not os.path.isdir(CLASSIC_WEBSITE_CISIS_PATH):
        raise exceptions.CisisPathNotFoundMigrationError(
            f"{CLASSIC_WEBSITE_CISIS_PATH} not found."
        )
    return CLASSIC_WEBSITE_CISIS_PATH


def check_migration_sources():
    paths = (
        CLASSIC_WEBSITE_BASES_WORK_PATH,
        CLASSIC_WEBSITE_BASES_XML_PATH,
        CLASSIC_WEBSITE_BASES_PDF_PATH,
        CLASSIC_WEBSITE_BASES_TRANSLATION_PATH,
        CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH,
    )
    names = (
        "CLASSIC_WEBSITE_BASES_WORK_PATH",
        "CLASSIC_WEBSITE_BASES_XML_PATH",
        "CLASSIC_WEBSITE_BASES_PDF_PATH",
        "CLASSIC_WEBSITE_BASES_TRANSLATION_PATH",
        "CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH",
    )
    for path, name in zip(paths, names):
        if not path:
            raise exceptions.MissingConfigurationError(f"Missing configuration: {name}")
        if not os.path.isdir(path):
            raise exceptions.MustBeDirectoryError(f"{name} must be a directory")


def get_paragraphs_id_file_path(article_pid):
    return os.path.join(
        os.path.dirname(CLASSIC_WEBSITE_BASES_PDF_PATH), "artigo", "p",
        article_pid[1:10], article_pid[10:14],
        article_pid[14:18], article_pid[-5:] + ".id",
    )


class DocumentFiles:

    def __init__(self, subdir_acron_issue, file_name, main_lang):
        self._subdir_acron_issue = subdir_acron_issue
        self._file_name = file_name
        self._main_lang = main_lang
        self._htdocs_img_revistas_files_paths = None
        self._bases_translation_files_paths = None
        self._bases_pdf_files_paths = None
        self._bases_xml_file_path = None

    @property
    def bases_translation_files_paths(self):
        """
        Obtém os arquivos HTML de bases/translation/acron/volnum/*filename*

        Returns
        -------
        dict
        {"en": {"front": "en_a01.html", "back": "en_ba01.html"},
         "es": {"front": "es_a01.html", "back": "es_ba01.html"}}
        """
        if self._bases_translation_files_paths is None:

            files = {}
            patterns = (f"??_{self._file_name}.htm*", f"??_b{self._file_name}.htm*")
            labels = ("front", "back")
            for label, pattern in zip(labels, patterns):
                paths = glob.glob(
                    os.path.join(
                        CLASSIC_WEBSITE_BASES_TRANSLATION_PATH, self._subdir_acron_issue, pattern)
                )
                if not paths:
                    continue
                # translations
                for path in paths:
                    basename = os.path.basename(path)
                    lang = basename[:2]
                    files.setdefault(lang, {})
                    files[lang][label] = path
            self._bases_translation_files_paths = files
        return self._bases_translation_files_paths

    @property
    def bases_pdf_files_paths(self):
        """
        Obtém os arquivos PDFs de bases/pdf/acron/volnum/*filename*.pdf

        Returns
        -------
        dict
        {"pt": "a01.pdf",
         "en": "en_a01.pdf",
         "es": "es_a01.pdf"}
        """
        if self._bases_pdf_files_paths is None:
            files = {}
            for pattern in (f"{self._file_name}.pdf", f"??_{self._file_name}.pdf"):
                paths = glob.glob(
                    os.path.join(
                        CLASSIC_WEBSITE_BASES_PDF_PATH,
                        self._subdir_acron_issue,
                        pattern
                    )
                )
                if not paths:
                    continue
                if "_" in pattern:
                    # translations
                    for path in paths:
                        basename = os.path.basename(path)
                        lang = basename[:2]
                        files[lang] = path
                else:
                    # main pdf
                    files[self._main_lang] = paths[0]
            self._bases_pdf_files_paths = files
        return self._bases_pdf_files_paths

    @property
    def htdocs_img_revistas_files_paths(self):
        """
        Obtém os arquivos de imagens de
        htdocs/img/revistas/acron/volnum/*filename*

        Returns
        -------
        list
            ["a01f01.jpg", "a01f02.jpg"],
        """
        if self._htdocs_img_revistas_files_paths is None:
            self._htdocs_img_revistas_files_paths = glob.glob(
                os.path.join(
                    CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH,
                    self._subdir_acron_issue,
                    f"*{self._file_name}*.*"
                )
            )
        return self._htdocs_img_revistas_files_paths

    @property
    def bases_xml_file_path(self):
        if self._bases_xml_file_path is None:
            try:
                xml_file_path = os.path.join(
                    CLASSIC_WEBSITE_BASES_XML_PATH,
                    self._subdir_acron_issue,
                    f"{self._file_name}.xml"
                )
                self._bases_xml_file_path = glob.glob(xml_file_path)[0]
            except IndexError:
                return None
        return self._bases_xml_file_path


def get_bases_acron(acron):
    return os.path.join(CLASSIC_WEBSITE_BASES_WORK_PATH, acron, acron)


def get_bases_artigo_path():
    return os.path.join(CLASSIC_WEBSITE_BASES_PATH, "artigo", "artigo")


def get_htdocs_path():
    return os.path.dirname(os.path.dirname(CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH))

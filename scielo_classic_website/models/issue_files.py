import os
import glob
import logging

from scielo_classic_website.utils.files_utils import create_zip_file
from scielo_classic_website import config


class ClassicWebsiteFileSystem:

    def __init__(self, acron, issue_folder, config):
        self.acron = acron
        self.issue_folder = issue_folder
        self._subdir_acron_issue = os.path.join(acron, issue_folder)
        self._htdocs_img_revistas_files = None
        self._bases_translation_files = None
        self._bases_pdf_files = None
        self._bases_xml_files = None
        self._config = config

    @property
    def files(self):
        if self.bases_xml_files:
            yield from self.bases_xml_files
        if self.bases_translation_files:
            yield from self.bases_translation_files
        if self.bases_pdf_files:
            yield from self.bases_pdf_files
        if self.htdocs_img_revistas_files:
            yield from self.htdocs_img_revistas_files

    @property
    def bases_translation_files(self):
        """
        Obtém os arquivos HTML de bases/translation/acron/volnum
        E os agrupa pelo nome do arquivo e idioma

        Returns
        -------
        dict which keys: paths, info
        "paths": [
            "/path/bases/translations/acron/volnum/pt_a01.htm",
            "/path/bases/translations/acron/volnum/pt_ba01.htm",
        ]
        "info": {
            "a01": {
                "pt": {"before": "pt_a01.htm",
                       "after": "pt_ba01.htm"}
            }
        }
        """
        if self._bases_translation_files is None:

            paths = glob.glob(
                os.path.join(
                    self._config["BASES_TRANSLATION_PATH"],
                    self._subdir_acron_issue, "*")
            )
            files = []
            for path in paths:
                basename = os.path.basename(path)
                name, ext = os.path.splitext(basename)
                lang = name[:2]
                name = name[3:]

                label = "before"
                if name[0] == "b":
                    name = name[1:]
                    label = "after"
                files.append(
                    {"type": "html",
                     "key": name, "path": path, "name": basename,
                     "lang": lang, "part": label}
                )
            self._bases_translation_files = files
        return self._bases_translation_files

    @property
    def bases_pdf_files(self):
        """
        Obtém os arquivos PDF de bases/pdf/acron/volnum
        E os agrupa pelo nome do arquivo e idioma

        Returns
        -------
        dict which keys: zip_file_path, files
        "files":
            {"a01":
                    {"pt": "a01.pdf",
                     "en": "en_a01.pdf",
                     "es": "es_a01.pdf"}
            }
        """
        if self._bases_pdf_files is None:

            paths = glob.glob(
                os.path.join(
                    self._config["BASES_PDF_PATH"],
                    self._subdir_acron_issue, "*")
            )
            files = []
            for path in paths:
                basename = os.path.basename(path)
                name, ext = os.path.splitext(basename)
                if name[2] == "_":
                    # translations
                    lang = name[:2]
                    name = name[3:]
                else:
                    # main pdf
                    lang = "main"
                files.append(
                    {"type": "pdf",
                     "key": name, "path": path, "name": basename,
                     "lang": lang}
                )
            self._bases_pdf_files = files
        return self._bases_pdf_files

    @property
    def htdocs_img_revistas_files(self):
        """
        Obtém os arquivos de imagens e outros de
        htdocs/img/revistas/acron/volnum/*
        htdocs/img/revistas/acron/volnum/*/*

        Returns
        -------
        dict
            zip_file_path
            files (original paths):
                {
                    path_completo_original: basename,
                    path_completo_original: basename,
                    path_completo_original: basename,
                    path_completo_original: basename,
                }
        """
        if self._htdocs_img_revistas_files is None:
            paths = glob.glob(
                os.path.join(
                    self._config["HTDOCS_IMG_REVISTAS_PATH"],
                    self._subdir_acron_issue,
                    "*"
                )
            )
            files = []
            for path in paths:
                if os.path.isfile(path):
                    files.append({
                        "type": "asset",
                        "path": path,
                        "name": os.path.basename(path)
                    })
                elif os.path.isdir(path):
                    for item in glob.glob(os.path.join(path, "*")):
                        files.append({
                            "type": "asset",
                            "path": item,
                            "name": os.path.basename(item)
                        })
            self._htdocs_img_revistas_files = files
        return self._htdocs_img_revistas_files

    @property
    def bases_xml_files(self):
        if self._bases_xml_files is None:
            paths = glob.glob(
                os.path.join(
                    self._config["BASES_XML_PATH"],
                    self._subdir_acron_issue,
                    "*.xml"
                )
            )
            files = []
            for path in paths:
                basename = os.path.basename(path)
                name, ext = os.path.splitext(basename)
                files.append(
                    {"type": "xml",
                     "key": name, "path": path, "name": basename,
                     }
                )
            self._bases_xml_files = files
        return self._bases_xml_files


class ArtigoDBPath:

    def __init__(self, classic_website, journal_acron, issue_folder):
        self.classic_website = classic_website
        self.journal_acron = journal_acron
        self.issue_folder = issue_folder

    def get_db_from_serial_base_xml_dir(self):
        items = []
        _serial_path = os.path.join(
            self.classic_website.serial_path,
            self.journal_acron, self.issue_folder, "base_xml", "id")

        if os.path.isdir(_serial_path):
            items.append(os.path.join(_serial_path, "i.id"))
            for item in os.listdir(_serial_path):
                if item != 'i.id' and item.endswith(".id"):
                    items.append(os.path.join(_serial_path, item))
        return items

    def get_db_from_serial_base_dir(self):
        items = []
        _serial_path = os.path.join(
            self.classic_website.serial_path,
            self.journal_acron, self.issue_folder, "base")

        if os.path.isdir(_serial_path):
            items.append(os.path.join(_serial_path, self.issue_folder))
        return items

    def get_db_from_bases_work_acron_id(self):
        items = []
        _bases_work_acron_path = os.path.join(
            self.classic_website.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        if os.path.isfile(_bases_work_acron_path + ".id"):
            items.append(_bases_work_acron_path + ".id")
        return items

    def get_db_from_bases_work_acron(self):
        items = []
        _bases_work_acron_path = os.path.join(
            self.classic_website.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        items.append(_bases_work_acron_path)
        return items

    def get_db_from_bases_work_acron_subset(self):
        items = []
        _bases_work_acron_path = os.path.join(
            self.classic_website.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        try:
            items.append(
                controller.isis_cmd.get_documents_by_issue_folder(
                    self.classic_website.cisis_path,
                    _bases_work_acron_path,
                    self.issue_folder)
            )
        except Exception as e:
            logging.exception(e)
        return items

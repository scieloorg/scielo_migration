import os
import glob

from scielo_classic_website.utils.files_utils import create_zip_file
from scielo_classic_website import config


class IssueFiles:

    def __init__(self, acron, issue_folder):
        self.acron = acron
        self.issue_folder = issue_folder
        self._subdir_acron_issue = os.path.join(acron, issue_folder)
        self._htdocs_img_revistas_files = None
        self._bases_translation_files = None
        self._bases_pdf_files = None
        self._bases_xml_files = None

    @property
    def bases_translation_files(self):
        """
        Cria um zip dos arquivos HTML de bases/translation/acron/volnum
        E os organiza num dicionário

        Returns
        -------
        dict which keys: zip_file_path, files
        files = {
            "a01": {
                "pt": {"before": "pt_a01.htm", "after": "pt_ba01.htm"}
            }
        }
        """
        if self._bases_translation_files is None:

            paths = glob.glob(
                os.path.join(
                    config.BASES_TRANSLATION_PATH,
                    self._subdir_acron_issue, "*")
            )
            zip_name = "_".join(
                ["translations", self.acron, self.issue_folder])
            zip_file_path = create_zip_file(
                paths, zip_name+".zip", zip_folder=None)

            document_files = {}
            for path in paths:
                basename = os.path.basename(path)
                name, ext = os.path.splitext(basename)
                lang = name[:2]
                name = name[3:]

                label = "before"
                if name[0] == "b":
                    name = name[1:]
                    label = "after"
                document_files.setdefault(name, {})
                document_files[name].setdefault(lang, {})
                document_files[name][lang][label] = basename
            self._bases_translation_files = {
                "zip_file_path": zip_file_path,
                "files": document_files,
            }
        return self._bases_translation_files

    @property
    def bases_pdf_files(self):
        """
        Cria um zip dos arquivos HTML de bases/translation/acron/volnum
        E os organiza num dicionário

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
                    config.BASES_PDF_PATH,
                    self._subdir_acron_issue, "*")
            )
            zip_name = "_".join(
                ["pdfs", self.acron, self.issue_folder])
            zip_file_path = create_zip_file(
                paths, zip_name+".zip", zip_folder=None)

            document_files = {}
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
                document_files.setdefault(name, {})
                document_files[name][lang] = basename
            self._bases_pdf_files = {
                "zip_file_path": zip_file_path,
                "files": document_files,
            }
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
                    config.HTDOCS_IMG_REVISTAS_PATH,
                    self._subdir_acron_issue,
                    "*"
                )
            )
            files = []
            for path in paths:
                if os.path.isfile(path):
                    files.append(path)
                elif os.path.isdir(path):
                    files.extend(glob.glob(os.path.join(path, "*")))

            zip_name = "_".join(
                ["img_revistas", self.acron, self.issue_folder])
            zip_file_path = create_zip_file(
                files, zip_name+".zip", zip_folder=None)

            self._htdocs_img_revistas_files = {
                "zip_file_path": zip_file_path,
                "files": {
                    file_path: os.path.basename(file_path)
                    for file_path in files
                }
            }
        return self._htdocs_img_revistas_files

    @property
    def bases_xml_files(self):
        if self._bases_xml_files is None:
            paths = os.path.join(
                config.BASES_XML_PATH,
                self._subdir_acron_issue,
                "*.xml"
            )
            zip_name = "_".join(
                ["xml", self.acron, self.issue_folder])
            zip_file_path = create_zip_file(
                paths, zip_name+".zip", zip_folder=None)

            files = {}
            for path in paths:
                basename = os.path.basename(path)
                name, ext = os.path.splitext(basename)
                files[name] = basename
            self._bases_xml_files = {
                "zip_file_path": zip_file_path,
                "files": files,
            }
        return self._bases_xml_files

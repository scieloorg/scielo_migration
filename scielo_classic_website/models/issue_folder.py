import glob
import logging
import os

from scielo_classic_website.htmlbody.html_body import HTMLFile
from scielo_classic_website.isisdb.isis_cmd import get_documents_by_issue_folder


def _get_classic_website_rel_path(file_path):
    for folder in (
        "bases",
        "htdocs",
    ):
        if folder in file_path:
            path = file_path[file_path.find(folder) + len(folder) :]
            return path


def fixed_glob(patterns, file_type, recursive):
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=recursive):
            item = {
                "pattern": pattern,
                "type": file_type,
            }
            try:
                item["original"] = path
                with open(path, "rb") as f:
                    item["content"] = f.read()
                item["fixed"] = path
            except Exception as e:
                item["error"] = str(e)
                item["error_type"] = type(e).__name__
            yield item


def get_files(patterns, file_type, recursive=False):
    for item in fixed_glob(patterns, file_type, recursive):
        try:
            if item.get("error"):
                yield item
                continue
            path = item["original"]
            basename = os.path.basename(item["fixed"])
            name, ext = os.path.splitext(basename)
            with open(path, "rb") as fp:
                content = fp.read()

            yield {
                "type": file_type,
                "original": item["original"],
                "path": item["fixed"],
                "key": name,
                "name": basename,
                "extension": ext,
                "relative_path": _get_classic_website_rel_path(item["fixed"]),
                "content": content,
            }
        
        except Exception as e:
            yield {"type": file_type, "error": str(e), "error_type": type(e).__name__}


class IssueFolder:
    def __init__(self, acron, issue_folder, classic_website_paths):
        self.acron = acron
        self.issue_folder = issue_folder
        self._subdir_acron_issue = os.path.join(acron, issue_folder)
        self._classic_website_paths = classic_website_paths
        self._exceptions = {}

    @property
    def exceptions(self):
        return self._exceptions

    @property
    def files(self):
        yield from self.bases_xml_files
        yield from self.bases_translation_files
        yield from self.bases_pdf_files
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
        pattern = os.path.join(
            self._classic_website_paths.bases_translation_path,
            self._subdir_acron_issue,
            "*",
        )
        for item in get_files([pattern], "html"):
            if item.get("error"):
                yield item
                continue
            try:
                key = item["key"]
                lang = key[:2]
                key = key[3:]
                part = "before"
                if key[0] == "b":
                    key = key[1:]
                    part = "after"

                item["key"] = key
                item["lang"] = lang
                item["part"] = part
                try:
                    item["replacements"] = HTMLFile(item.pop("original")).asset_path_fixes
                except KeyError:
                    item["replacements"] =  {}
                yield item
            
            except Exception as e:
                yield {"type": "html", "error": str(e), "error_type": type(e).__name__}

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
        pattern = os.path.join(
            self._classic_website_paths.bases_pdf_path,
            self._subdir_acron_issue,
            "*",
        )
        for item in get_files([pattern], "pdf"):
            if item.get("error"):
                yield item
                continue
            try:
                key = item["key"]
                if "_" in key and key[2] == "_":
                    # translations
                    lang = key[:2]
                    key = key[3:]
                    item["key"] = key
                else:
                    # main pdf
                    lang = None
            except IndexError as e:
                continue
            try:
                item["lang"] = lang
                yield item
            except Exception as e:
                yield {"type": "pdf", "error": str(e), "error_type": type(e).__name__}

    @property
    def htdocs_img_revistas_files(self):
        """
        Obtém os arquivos de imagens e outros de
        htdocs/img/revistas/acron/volnum/*
        htdocs/img/revistas/acron/volnum/*/*

        Returns
        -------
        list: Lista de arquivos encontrados
        """
        file_type = "asset"
        htdocs_img_revistas_path = self._classic_website_paths.htdocs_img_revistas_path

        htdocs_path = os.path.dirname(
            os.path.dirname(htdocs_img_revistas_path)
        )

        patterns = [
            os.path.join(htdocs_path, "**", self._subdir_acron_issue, "*.*"),
            os.path.join(htdocs_path, "**", self._subdir_acron_issue, "*", "*.*"),
        ]

        for item in get_files(patterns, "asset", True):
            if item.get("error"):
                yield item
                continue
            try:
                path = item.pop("original")
                if os.path.isfile(path):
                    # Arquivo direto
                    yield item
            except Exception as e:
                yield {"type": "asset", "error": str(e), "error_type": type(e).__name__}

    @property
    def bases_xml_files(self):
        patterns = [
            os.path.join(
                self._classic_website_paths.bases_xml_path,
                self._subdir_acron_issue,
                "*.xml",
            )
        ]
        for item in get_files(patterns, "xml"):
            try:
                yield item
            except Exception as e:
                yield {"type": "xml", "error": str(e), "error_type": type(e).__name__}


class ArtigoDBPath:
    def __init__(self, classic_website_paths, journal_acron, issue_folder):
        self.classic_website_paths = classic_website_paths
        self.journal_acron = journal_acron
        self.issue_folder = issue_folder

    def get_artigo_db_path(self):
        # ordem de preferencia para obter os arquivos de base de dados isis
        # que contém registros dos artigos
        callables = (
            self.get_db_from_serial_base_xml_dir,
            self.get_db_from_bases_work_acron_id,
            self.get_db_from_serial_base_dir,
            self.get_db_from_bases_work_acron_subset,
            self.get_db_from_bases_work_acron,
        )
        for func in callables:
            try:
                files = func()
                if files:
                    return files
            except Exception as e:
                logging.exception(e)
                continue
        return []

    def get_db_from_serial_base_xml_dir(self):
        items = []
        _serial_path = os.path.join(
            self.classic_website_paths.serial_path,
            self.journal_acron,
            self.issue_folder,
            "base_xml",
            "id",
        )

        if os.path.isdir(_serial_path):
            items.append(os.path.join(_serial_path, "i.id"))
            for item in os.listdir(_serial_path):
                if item != "i.id" and item.endswith(".id"):
                    items.append(os.path.join(_serial_path, item))
        return items

    def get_db_from_serial_base_dir(self):
        items = []
        _serial_path = os.path.join(
            self.classic_website_paths.serial_path,
            self.journal_acron,
            self.issue_folder,
            "base",
        )

        if os.path.isdir(_serial_path):
            items.append(os.path.join(_serial_path, self.issue_folder))
        return items

    def get_db_from_bases_work_acron_id(self):
        items = []
        _bases_work_acron_path = os.path.join(
            self.classic_website_paths.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        if os.path.isfile(_bases_work_acron_path + ".id"):
            items.append(_bases_work_acron_path + ".id")
        return items

    def get_db_from_bases_work_acron(self):
        items = []
        _bases_work_acron_path = os.path.join(
            self.classic_website_paths.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        items.append(_bases_work_acron_path)
        return items

    def get_db_from_bases_work_acron_subset(self):
        items = []
        _bases_work_acron_path = os.path.join(
            self.classic_website_paths.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        try:
            items.append(
                get_documents_by_issue_folder(
                    self.classic_website_paths.cisis_path,
                    _bases_work_acron_path,
                    self.issue_folder,
                )
            )
        except Exception as e:
            logging.exception(e)
        return items

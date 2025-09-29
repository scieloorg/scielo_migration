import glob
import logging
import os
from datetime import datetime

from scielo_classic_website.htmlbody.html_body import HTMLContent
from scielo_classic_website.isisdb.isis_cmd import get_documents_by_issue_folder


def try_to_fix_encoding(nome_original):
    try:
        nome_bytes = nome_original.encode("utf-8", errors="surrogateescape")
        return (
            nome_bytes.decode("cp1252") if isinstance(nome_bytes, bytes) else nome_bytes
        )
    except Exception as exc:
        logging.exception(exc)
        return nome_original


def modified_date(file_path):
    try:
        stat = os.stat(file_path)
        return datetime.fromtimestamp(stat.st_mtime).isoformat()
    except Exception as e:
        return None


def _get_classic_website_rel_path(file_path):
    for folder in (
        "bases",
        "htdocs",
    ):
        if folder in file_path:
            path = file_path[file_path.find(folder):]
            return path


def fixed_glob(patterns, file_type, recursive):
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=recursive):
            try:
                item = {
                    "type": file_type,
                }
                item["path"] = path
                with open(path, "rb") as f:
                    item["content"] = f.read()
                item["modified_date"] = modified_date(path)
            except Exception as e:
                logging.exception(e)
                item["error"] = str(e)
                item["error_type"] = type(e).__name__
            yield item


def get_files(patterns, file_type, recursive=False):
    for item in fixed_glob(patterns, file_type, recursive):
        try:
            if not item.get("error"):
                path = item["path"]
                item["name"] = os.path.basename(path)
                item["key"], item["extension"] = os.path.splitext(item["name"])
                item["type"] = file_type
                item["relative_path"] = _get_classic_website_rel_path(path)
            yield  item

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
                    hc = HTMLContent(item["content"])
                    if hc.asset_path_fixes:
                        item["content"] = hc.content
                except KeyError:
                    pass
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

        htdocs_path = os.path.dirname(os.path.dirname(htdocs_img_revistas_path))

        patterns = [
            os.path.join(htdocs_path, "**", self._subdir_acron_issue, "*.*"),
            os.path.join(htdocs_path, "**", self._subdir_acron_issue, "*", "*.*"),
        ]

        for item in get_files(patterns, "asset", True):
            if item.get("error"):
                yield item
                continue
            try:
                if os.path.isfile(item["path"]):
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

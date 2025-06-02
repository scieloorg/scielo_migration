import glob
import logging
import os

from scielo_classic_website.htmlbody.html_body import HTMLFile
from scielo_classic_website.isisdb.isis_cmd import get_documents_by_issue_folder
from scielo_classic_website.utils.files_utils import create_zip_file


def _get_classic_website_rel_path(file_path):
    for folder in (
        "bases",
        "htdocs",
    ):
        if folder in file_path:
            path = file_path[file_path.find(folder) + len(folder) :]
            return path


class IssueFiles:
    def __init__(self, acron, issue_folder, classic_website_paths):
        self.acron = acron
        self.issue_folder = issue_folder
        self._subdir_acron_issue = os.path.join(acron, issue_folder)
        self._htdocs_img_revistas_files = None
        self._bases_translation_files = None
        self._bases_pdf_files = None
        self._bases_xml_files = None
        self._classic_website_paths = classic_website_paths
        self._exceptions = {}

    @property
    def exceptions(self):
        return self._exceptions

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
                    self._classic_website_paths.bases_translation_path,
                    self._subdir_acron_issue,
                    "*",
                )
            )
            files = []
            for path in paths:
                try:
                    basename = os.path.basename(path)
                    name, ext = os.path.splitext(basename)
                    lang = name[:2]
                    name = name[3:]
                    label = "before"
                    if name[0] == "b":
                        name = name[1:]
                        label = "after"

                    files.append(
                        {
                            "type": "html",
                            "key": name,
                            "path": path,
                            "name": basename,
                            "relative_path": _get_classic_website_rel_path(path),
                            "lang": lang,
                            "part": label,
                            "replacements": HTMLFile(path).asset_path_fixes,
                        }
                    )
                except Exception as e:
                    self._exceptions.setdefault("bases_translation_files", [])
                    self._exceptions["bases_translation_files"].append(
                        {"message": str(e), "type": type(e).__name__}
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
                    self._classic_website_paths.bases_pdf_path,
                    self._subdir_acron_issue,
                    "*",
                )
            )
            files = []
            for path in paths:
                try:
                    basename = os.path.basename(path)
                    name, ext = os.path.splitext(basename)
                    try:
                        if "_" in name and name[2] == "_":
                            # translations
                            lang = name[:2]
                            name = name[3:]
                        else:
                            # main pdf
                            lang = None
                    except IndexError as e:
                        logging.info(path)
                        logging.exception(e)
                        continue
                    files.append(
                        {
                            "type": "pdf",
                            "key": name,
                            "path": path,
                            "name": basename,
                            "relative_path": _get_classic_website_rel_path(path),
                            "lang": lang,
                        }
                    )
                except Exception as e:
                    self._exceptions.setdefault("bases_pdf_files", [])
                    self._exceptions["bases_pdf_files"].append(
                        {"message": str(e), "type": type(e).__name__}
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
        list: Lista de arquivos encontrados
        """
        if self._htdocs_img_revistas_files is None:
            self._htdocs_img_revistas_files = self.get_files_from_path(
                self._classic_website_paths.htdocs_img_revistas_path,
                file_type="asset",
                exception_key="htdocs_img_revistas_files",
            )
        return self._htdocs_img_revistas_files

    def get_files_from_path(self, base_path, file_type="asset", exception_key=None):
        """
        Método genérico para buscar arquivos em um caminho específico.
        Busca arquivos em base_path/acron/issue_folder/* e subdiretórios.

        Args:
            base_path: Caminho base onde buscar
            file_type: Tipo de arquivo para o campo "type" no resultado
            exception_key: Chave para armazenar exceções no dict _exceptions

        Returns:
            list: Lista de arquivos encontrados
        """
        if not base_path or not os.path.exists(base_path):
            return []

        files = []
        if base_path.endswith(self._subdir_acron_issue):
            paths = glob.glob(os.path.join(base_path, "*"))
        else:
            paths = glob.glob(os.path.join(base_path, self._subdir_acron_issue, "*"))

        for path in paths:
            try:
                if os.path.isfile(path):
                    # Arquivo direto
                    files.append(
                        {
                            "type": file_type,
                            "path": path,
                            "relative_path": _get_classic_website_rel_path(path),
                            "name": os.path.basename(path),
                        }
                    )
                elif os.path.isdir(path):
                    # Diretório - busca arquivos dentro
                    for item in glob.glob(os.path.join(path, "*")):
                        if os.path.isfile(item):
                            files.append(
                                {
                                    "type": file_type,
                                    "path": item,
                                    "relative_path": _get_classic_website_rel_path(
                                        item
                                    ),
                                    "name": os.path.basename(item),
                                }
                            )

            except Exception as e:
                if exception_key:
                    self._exceptions.setdefault(exception_key, [])
                    self._exceptions[exception_key].append(
                        {"path": path, "message": str(e), "type": type(e).__name__}
                    )

        return files

    @property
    def bases_xml_files(self):
        if self._bases_xml_files is None:
            paths = glob.glob(
                os.path.join(
                    self._classic_website_paths.bases_xml_path,
                    self._subdir_acron_issue,
                    "*.xml",
                )
            )
            files = []
            for path in paths:
                basename = os.path.basename(path)
                name, ext = os.path.splitext(basename)
                try:
                    files.append(
                        {
                            "type": "xml",
                            "key": name,
                            "path": path,
                            "name": basename,
                            "relative_path": _get_classic_website_rel_path(path),
                        }
                    )
                except Exception as e:
                    self._exceptions.setdefault("bases_xml_files", [])
                    self._exceptions["bases_xml_files"].append(
                        {"message": str(e), "type": type(e).__name__}
                    )
            self._bases_xml_files = files
        return self._bases_xml_files


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


class ArtigoRecordsPath:
    def __init__(self, classic_website_paths, journal_acron):
        self.classic_website_paths = classic_website_paths
        self.journal_acron = journal_acron

    def get_db_from_serial_base_xml_dir(self, issue_folder):
        _serial_path = os.path.join(
            self.classic_website_paths.serial_path,
            self.journal_acron,
            issue_folder,
            "base_xml",
            "id",
        )
        if os.path.isdir(_serial_path):
            yield os.path.join(_serial_path, "i.id")
            for item in os.listdir(_serial_path):
                if item != "i.id" and item.endswith(".id"):
                    yield os.path.join(_serial_path, item)

    def get_db_from_serial_base_dir(self, issue_folder):
        _serial_path = os.path.join(
            self.classic_website_paths.serial_path,
            self.journal_acron,
            issue_folder,
            "base",
        )
        path = os.path.join(_serial_path, issue_folder)
        if os.path.isfile(path + ".mst"):
            yield path

    def get_db_from_bases_work_acron_id(self):
        _bases_work_acron_path = os.path.join(
            self.classic_website_paths.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        if os.path.isfile(_bases_work_acron_path + ".id"):
            yield _bases_work_acron_path + ".id"

    def get_db_from_bases_work_acron(self):
        path = os.path.join(
            self.classic_website_paths.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        if os.path.isfile(path + ".mst"):
            yield path

    def get_db_from_bases_work_acron_subset(self, issue_folder):
        _bases_work_acron_path = os.path.join(
            self.classic_website_paths.bases_work_path,
            self.journal_acron,
            self.journal_acron,
        )
        try:
            yield get_documents_by_issue_folder(
                self.classic_website_paths.cisis_path,
                _bases_work_acron_path,
                issue_folder,
            )
        except Exception as e:
            logging.exception(e)

import logging

from scielo_classic_website import controller, config
from scielo_classic_website.models.issue_files import (
    ClassicWebsiteFileSystem,
    ArtigoDBPath,
)

# Para Journal, Issue, Document devem ficar disponíveis neste módulo
from scielo_classic_website.models.journal import Journal
from scielo_classic_website.models.issue import Issue
from scielo_classic_website.models.document import Document


def get_document_pids(from_date, to_date):
    return controller.isis_cmd.get_document_pids(from_date, to_date)


def get_paragraphs_records(pid):
    id_file_path = config.get_paragraphs_id_file_path(pid)
    return controller.pids_and_their_records(id_file_path, "artigo")


def get_records_by_pid(pid):
    source_path = controller.isis_cmd.get_document_isis_db(pid)
    return controller.pids_and_their_records(source_path, "artigo")


def get_records_by_acron(acron, id_folder_path=None):
    source_path = controller.get_acron_db_path(acron, id_folder_path)
    return controller.pids_and_their_records(source_path, "artigo")


def get_records_by_source_path(db_type, source_path):
    return controller.pids_and_their_records(source_path, db_type)


def get_issue_files(acron, issue_folder, config):
    classic_ws_fs = ClassicWebsiteFileSystem(acron, issue_folder, config)
    return classic_ws_fs.files


def get_artigo_db_path(acron, issue_folder, config):
    artigo_db_path = ArtigoDBPath(config, acron, issue_folder)

    # ordem de preferencia para obter os arquivos de base de dados isis que 
    # contém registros dos artigos
    callables = (
        artigo_db_path.get_db_from_serial_base_xml_dir,
        artigo_db_path.get_db_from_bases_work_acron_id,
        artigo_db_path.get_db_from_serial_base_dir,
        artigo_db_path.get_db_from_bases_work_acron_subset,
        artigo_db_path.get_db_from_bases_work_acron,
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

from scielo_classic_website import controller, config
from scielo_classic_website.models.issue_files import IssueFiles

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


def get_issue_files(acron, issue_folder):
    issue_files = IssueFiles(acron, issue_folder)
    files = dict(
        img=issue_files.htdocs_img_revistas_files,
        pdf=issue_files.bases_pdf_files,
    )
    if issue_files.bases_xml_files:
        files["xml"] = issue_files.bases_xml_files
    else:
        files["html"] = issue_files.bases_translation_files
    return files

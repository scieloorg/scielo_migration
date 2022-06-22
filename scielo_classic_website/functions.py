from scielo_classic_website import controller
from scielo_classic_website.iid2json import id2json3


def get_paragraphs_id_file_path():
    pass


def get_records_by_pid(pid):
    source_path = controller.get_document_isis_db(pid)
    return controller.pids_and_their_records(source_path, id2json3.article_id)


def get_records_by_acron(acron, id_folder_path=None):
    source_path = controller.get_acron_db_path(acron, id_folder_path)
    return controller.pids_and_their_records(source_path, id2json3.article_id)


def get_records_by_source_path(db_type, source_path):
    id_function = id2json3.article_id
    if db_type == "title":
        id_function = id2json3.journal_id
    elif db_type == "issue":
        id_function = id2json3.issue_id

    return controller.pids_and_their_records(source_path, id_function)

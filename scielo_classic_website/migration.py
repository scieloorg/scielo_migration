from scielo_classic_website import controller


def get_document_pids_to_migrate(from_date, to_date):
    return controller.isis_cmd.get_document_pids_to_migrate(from_date, to_date)


def get_paragraphs_records():
    pass


def get_records_by_pid(pid):
    source_path = controller.isis_cmd.get_document_isis_db(pid)
    return controller.pids_and_their_records(source_path, "artigo")


def get_records_by_acron(acron, id_folder_path=None):
    source_path = controller.get_acron_db_path(acron, id_folder_path)
    return controller.pids_and_their_records(source_path, "artigo")


def get_records_by_source_path(db_type, source_path):
    return controller.pids_and_their_records(source_path, db_type)

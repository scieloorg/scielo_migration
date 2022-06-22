from scielo_classic_website.iid2json import id2json3

from scielo_classic_website.isis_cmds import (
    create_id_file,
    get_id_file_path,
    get_document_isis_db,
    get_document_pids_to_migrate,
)


def _pids_and_their_records(source_file_path, id_function):
    records = _get_records(source_file_path)
    return id2json3.get_id_and_json_records(records, id_function)


def _get_records(source_file_path=None, records_content=None):
    """
    Get ISIS data from `source_file_path` or `records_content`
    which is ISIS database or ID file

    Parameters
    ----------
    source_file_path: str
        ISIS database or ID file path
    records_content: str
        ID records

    Returns
    -------
    generator
        results of the migration
    """
    if source_file_path:
        # get id_file_path
        id_file_path = get_id_file_path(source_file_path)

        # get id file rows
        rows = id2json3.get_id_file_rows(id_file_path)
    elif records_content:
        rows = records_content.splitlines()
    else:
        raise ValueError(
            "Unable to migrate ISIS DB. "
            "Expected `source_file_path` or `records_content`."
        )

    # migrate
    return id2json3.join_id_file_rows_and_return_records(rows)


def get_records_by_pid(pid):
    source_path = get_document_isis_db(pid)
    return _pids_and_their_records(source_path, id2json3.article_id)


def _get_acron_db_path(acron, id_folder_path=None):
    config.check_migration_sources()

    db_path = config.get_bases_acron(acron)
    print("db:", db_path)
    if id_folder_path:
        id_file_path = os.path.join(id_folder_path, f"{acron}.id")
        id_file_path = create_id_file(db_path, id_file_path)
        db_path = id_file_path
        print(f"{id_file_path} - size: {size(id_file_path)} bytes")
    return db_path


def get_records_by_acron(acron, id_folder_path=None):
    source_path = _get_acron_db_path(acron, id_folder_path)
    return _pids_and_their_records(source_path, id2json3.article_id)


def get_records_by_source_path(db_type, source_path):
    id_function = id2json3.article_id
    if db_type == "title":
        id_function = id2json3.journal_id
    elif db_type == "issue":
        id_function = id2json3.issue_id

    return _pids_and_their_records(source_path, id_function)

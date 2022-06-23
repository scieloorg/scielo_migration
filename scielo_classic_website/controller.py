from scielo_classic_website.iid2json import id2json3

from scielo_classic_website import isis_cmd


def pids_and_their_records(source_file_path, db_type):
    if not source_file_path:
        return []

    id_function = id2json3.article_id
    if db_type == "title":
        id_function = id2json3.journal_id
    elif db_type == "issue":
        id_function = id2json3.issue_id

    # get id_file_path
    id_file_path = isis_cmd.get_id_file_path(source_file_path)
    return id2json3.pids_and_their_records(id_file_path, id_function)


def get_acron_db_path(acron, id_folder_path=None):
    config.check_migration_sources()

    db_path = config.get_bases_acron(acron)
    print("db:", db_path)
    if id_folder_path:
        id_file_path = os.path.join(id_folder_path, f"{acron}.id")
        id_file_path = isis_cmd.create_id_file(db_path, id_file_path)
        db_path = id_file_path
        print(f"{id_file_path} - size: {size(id_file_path)} bytes")
    return db_path

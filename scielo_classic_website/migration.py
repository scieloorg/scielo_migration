# from scielo_classic_website import config, controller
# from scielo_classic_website.models.issue_files import IssueFiles


# def get_document_pids(from_date, to_date):
#     return controller.isis_cmd.get_document_pids(from_date, to_date)


# def get_paragraphs_records(pid):
#     id_file_path = config.get_paragraphs_id_file_path(pid)
#     return controller.pids_and_their_records(id_file_path, "artigo")


# def get_records_by_pid(pid):
#     source_path = controller.isis_cmd.get_document_isis_db(pid)
#     return controller.pids_and_their_records(source_path, "artigo")


# def get_records_by_source_path(db_type, source_path):
#     return controller.pids_and_their_records(source_path, db_type)


# def get_issue_files(acron, issue_folder):
#     issue_files = IssueFiles(acron, issue_folder)
#     return issue_files.files

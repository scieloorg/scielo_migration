import logging
import os

from scielo_classic_website.iid2json import id2json3
from scielo_classic_website.isisdb.isis_cmd import ISISCommader
from scielo_classic_website.models.document import Document
from scielo_classic_website.models.issue import Issue
from scielo_classic_website.models.issue_files import (
    ArtigoDBPath,
    ArtigoRecordsPath,
    IssueFiles,
)
from scielo_classic_website.models.journal import Journal


class ClassicWebsitePaths:
    def __init__(
        self,
        bases_path,
        bases_work_path,
        bases_translation_path,
        bases_pdf_path,
        bases_xml_path,
        htdocs_img_revistas_path,
        serial_path,
        cisis_path,
        title_path,
        issue_path,
    ):
        self.bases_path = bases_path
        self.bases_work_path = bases_work_path
        self.bases_pdf_path = bases_pdf_path
        self.bases_translation_path = bases_translation_path
        self.bases_xml_path = bases_xml_path
        self.htdocs_img_revistas_path = htdocs_img_revistas_path
        self.serial_path = serial_path
        self.cisis_path = cisis_path
        self.title_path = title_path
        self.issue_path = issue_path
        self.BASES_ARTIGO_PATH = os.path.join(self.bases_path, "artigo", "artigo")

    def get_paragraphs_id_file_path(self, article_pid):
        if article_pid and len(article_pid) == 23:
            return os.path.join(
                self.bases_path,
                "artigo",
                "p",
                article_pid[1:10],
                article_pid[10:14],
                article_pid[14:18],
                article_pid[-5:] + ".id",
            )

    @property
    def id_files(self):
        artigo_p_path = os.path.join(self.bases_path, "artigo", "p")
        for issn in os.listdir(artigo_p_path):
            issn_path = os.path.join(artigo_p_path, issn)
            for year in os.listdir(issn_path):
                year_path = os.path.join(issn_path, year)
                for issue_id in os.listdir(year_path):
                    issue_id_path = os.path.join(year_path, issue_id)
                    for id_file in os.listdir(issue_id_path):
                        yield os.path.join(issue_id_path, id_file)


class ClassicWebsite:
    def __init__(
        self,
        bases_path,
        bases_work_path,
        bases_translation_path,
        bases_pdf_path,
        bases_xml_path,
        htdocs_img_revistas_path,
        serial_path,
        cisis_path,
        title_path,
        issue_path,
    ):
        self.classic_website_paths = ClassicWebsitePaths(
            bases_path,
            bases_work_path,
            bases_translation_path,
            bases_pdf_path,
            bases_xml_path,
            htdocs_img_revistas_path,
            serial_path,
            cisis_path,
            title_path,
            issue_path,
        )
        self.isis_commander = ISISCommader(self.classic_website_paths)
        self.data = {}

    def get_issue_files(self, acron, issue_folder):
        classic_ws_fs = IssueFiles(acron, issue_folder, self.classic_website_paths)
        return classic_ws_fs.files

    def get_issue_files_and_exceptions(self, acron, issue_folder):
        issue_files = IssueFiles(acron, issue_folder, self.classic_website_paths)
        return {"files": issue_files.files, "exceptions": issue_files.exceptions}

    def get_journals_pids_and_records(self):
        id_file_path = self.isis_commander.get_id_file_path(
            self.classic_website_paths.title_path
        )
        return id2json3.pids_and_their_records(id_file_path, "title")

    def get_issues_pids_and_records(self):
        id_file_path = self.isis_commander.get_id_file_path(
            self.classic_website_paths.issue_path
        )
        return id2json3.pids_and_their_records(id_file_path, "issue")

    def get_p_records(self, pid):
        p_records = []
        if len(pid) != 23:
            raise ValueError(f"Found pid={pid} invalid size ({len(pid)})")

        id_file_path = self.classic_website_paths.get_paragraphs_id_file_path(pid)
        for p_pids, p_records in id2json3.pids_and_their_records(
            id_file_path, "artigo"
        ):
            return pid, p_records

    @property
    def p_records(self):
        for id_file_path in self.classic_website_paths.id_files:
            logging.info(f"p_records from id_file_path={id_file_path}")
            yield from id2json3.pids_and_their_records(id_file_path, "artigo")

    def get_documents_pids_and_records(
        self,
        acron,
        issue_folder=None,
        issue_pid=None,
    ):
        logging.info(f"ClassicWebsite.get_documents_pids_and_records {acron} {issue_folder} {issue_pid}")
        article_db_path = ArtigoRecordsPath(self.classic_website_paths, acron)
        source_paths = None
        found = False
        if issue_folder:
            funcs = (
                article_db_path.get_db_from_serial_base_xml_dir,
                article_db_path.get_db_from_bases_work_acron_subset,
                article_db_path.get_db_from_serial_base_dir,
            )
            for func in funcs:
                source_paths = func(issue_folder)
                if source_paths:
                    break

            if source_paths:
                for source_path in source_paths:
                    logging.info(f"Source: {source_path}")
                    id_file_path = self.isis_commander.get_id_file_path(source_path)
                    for doc_id, records in id2json3.pids_and_their_records(id_file_path, "artigo"):
                        logging.info(f"issue_pid: {issue_pid}, doc_id: {doc_id}")
                        yield doc_id, records
                        found = True

        if not found and issue_pid:
            funcs = (
                article_db_path.get_db_from_bases_work_acron_id,
                article_db_path.get_db_from_bases_work_acron,
            )
            for func in funcs:
                source_paths = func()
                if source_paths:
                    break

        if not source_paths:
            raise FileNotFoundError(
                f"Unable to find document records of {acron} {issue_folder} {issue_pid}"
            )

        for source_path in source_paths:
            logging.info(f"Source: {source_path}")
            id_file_path = self.isis_commander.get_id_file_path(source_path)
            for doc_id, records in id2json3.pids_and_their_records(id_file_path, "artigo"):
                logging.info(f"issue_pid: {issue_pid}, doc_id: {doc_id}")
                if issue_pid in doc_id:
                    logging.info("found records")
                    yield doc_id, records

    def get_source_paths(
        self,
        acron,
        issue_folder=None,
        issue_pid=None,
    ):
        logging.info(f"ClassicWebsite.get_source_paths {acron} {issue_folder} {issue_pid}")
        article_db_path = ArtigoRecordsPath(self.classic_website_paths, acron)
        source_paths = None
        found = False
        if issue_folder:
            funcs = (
                article_db_path.get_db_from_serial_base_xml_dir,
                article_db_path.get_db_from_bases_work_acron_subset,
                article_db_path.get_db_from_serial_base_dir,
            )
            for func in funcs:
                source_paths = func(issue_folder)
                if source_paths:
                    return source_paths

        if not found and issue_pid:
            funcs = (
                article_db_path.get_db_from_bases_work_acron_id,
                article_db_path.get_db_from_bases_work_acron,
            )
            for func in funcs:
                source_paths = func(issue_folder)
                if source_paths:
                    return source_paths

    def get_document_records(
        self,
        source_paths,
    ):
        for source_path in source_paths:
            logging.info(f"ClassicWebsite.get_document_records: {source_path}")
            id_file_path = self.isis_commander.get_id_file_path(source_path)
            yield from id2json3.pids_and_their_records(id_file_path, "artigo")

    def get_issue_doc_records(
        self,
        acron,
        issue_folder=None,
        issue_pid=None,
    ):
        issues = {}
        source_paths = self.get_source_paths( acron, issue_folder, issue_pid)
        for item_id, records in self.get_document_records(source_paths):
            record_type = id2json3._get_value(records[0], "v706")
            if record_type == "i":
                issues[item_id] = records
            elif record_type == "o":
                if len(item_id) == 23:
                    i_id = item_id[1:18]
                    yield {"issue_id": i_id, "doc_id": item_id, "issue": issues.get(i_id), "article": records}
                else:
                    yield {"invalid_records": True, "id": item_id, "records": records}
            else:
                yield {"invalid_records": True, "id": item_id, "records": records}

import os

from scielo_classic_website.models.issue_files import IssueFiles, ArtigoDBPath
from scielo_classic_website.iid2json import id2json3
from scielo_classic_website.isisdb.isis_cmd import ISISCommader
from scielo_classic_website.models.journal import Journal
from scielo_classic_website.models.issue import Issue
from scielo_classic_website.models.document import Document


class ClassicWebsitePaths:

    def __init__(self,
                 bases_path,
                 bases_translation_path, bases_pdf_path, bases_xml_path,
                 htdocs_img_revistas_path,
                 serial_path,
                 cisis_path,
                 title_path,
                 issue_path,
                 ):
        self.bases_path = bases_path
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
        return os.path.join(
            self.bases_path, "artigo", "p",
            article_pid[1:10], article_pid[10:14],
            article_pid[14:18], article_pid[-5:] + ".id",
        )


class ClassicWebsite:

    def __init__(self,
                 bases_path,
                 bases_translation_path, bases_pdf_path, bases_xml_path,
                 htdocs_img_revistas_path,
                 serial_path,
                 cisis_path,
                 title_path,
                 issue_path,
                 ):
        self.classic_website_paths = ClassicWebsitePaths(
            bases_path,
            bases_translation_path, bases_pdf_path, bases_xml_path,
            htdocs_img_revistas_path,
            serial_path,
            cisis_path,
            title_path,
            issue_path,
        )
        self.isis_commander = ISISCommader(self.classic_website_paths)

    def get_issue_files(self, acron, issue_folder):
        classic_ws_fs = IssueFiles(acron, issue_folder, self.classic_website_paths)
        return classic_ws_fs.files

    def get_journals_pids_and_records(self):
        id_file_path = self.isis_commander.get_id_file_path(
            self.classic_website_paths.title_path)
        return id2json3.pids_and_their_records(id_file_path, "title")

    def get_issues_pids_and_records(self):
        id_file_path = self.isis_commander.get_id_file_path(
            self.classic_website_paths.issue_path)
        return id2json3.pids_and_their_records(id_file_path, "issue")

    def get_documents_pids_and_records(self, acron, issue_folder):
        article_db_path = ArtigoDBPath(self.classic_website_paths, acron, issue_folder)
        for source_path in article_db_path.get_artigo_db_path():
            id_file_path = self.isis_commander.get_id_file_path(source_path)
            pids_and_records = id2json3.pids_and_their_records(
                id_file_path, "artigo")
            for pid, records in pids_and_records:
                id_file_path = self.classic_website_paths.get_paragraphs_id_file_path(pid)
                p_pids, p_records = id2json3.pids_and_their_records(
                    id_file_path, "artigo")
                if not p_records:
                    p_records = []
                yield (pid, records + p_records)

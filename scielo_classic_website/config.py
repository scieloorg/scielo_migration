import os
import glob


from scielo_classic_website import exceptions



ATTRIBUTES_PATH = os.environ.get("ATTRIBUTES_PATH", 'scielo_classic_website/settings/attributes')

# /var/www/scielo/proc/cisis
CLASSIC_WEBSITE_CISIS_PATH = os.environ.get("CLASSIC_WEBSITE_CISIS_PATH")

CLASSIC_WEBSITE_BASES_WORK_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_WORK_PATH")
CLASSIC_WEBSITE_BASES_XML_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_XML_PATH")
CLASSIC_WEBSITE_BASES_PDF_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_PDF_PATH")
CLASSIC_WEBSITE_BASES_TRANSLATION_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_TRANSLATION_PATH")
CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH = os.environ.get("CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH")
CLASSIC_WEBSITE_BASES_PATH = os.environ.get("CLASSIC_WEBSITE_BASES_PATH")


CLASSIC_WEBSITE_MIGRATION_CELERY_BROKER_URL = os.environ.get(
    "CLASSIC_WEBSITE_MIGRATION_CELERY_BROKER_URL", 'amqp://guest@0.0.0.0:5672//')
CLASSIC_WEBSITE_MIGRATION_CELERY_RESULT_BACKEND_URL = os.environ.get(
    "CLASSIC_WEBSITE_MIGRATION_CELERY_RESULT_BACKEND_URL", 'rpc://')


def get_cisis_path():
    """
    Get CLASSIC_WEBSITE_CISIS_PATH
    """
    if not CLASSIC_WEBSITE_CISIS_PATH:
        raise exceptions.MissingCisisPathEnvVarError(
            "Missing value for environment variable CLASSIC_WEBSITE_CISIS_PATH. "
            "CLASSIC_WEBSITE_CISIS_PATH=/var/www/scielo/proc/cisis"
        )
    if not os.path.isdir(CLASSIC_WEBSITE_CISIS_PATH):
        raise exceptions.CisisPathNotFoundMigrationError(
            f"{CLASSIC_WEBSITE_CISIS_PATH} not found."
        )
    return CLASSIC_WEBSITE_CISIS_PATH


def check_migration_sources():
    paths = (
        CLASSIC_WEBSITE_BASES_WORK_PATH,
        CLASSIC_WEBSITE_BASES_XML_PATH,
        CLASSIC_WEBSITE_BASES_PDF_PATH,
        CLASSIC_WEBSITE_BASES_TRANSLATION_PATH,
        CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH,
    )
    names = (
        "CLASSIC_WEBSITE_BASES_WORK_PATH",
        "CLASSIC_WEBSITE_BASES_XML_PATH",
        "CLASSIC_WEBSITE_BASES_PDF_PATH",
        "CLASSIC_WEBSITE_BASES_TRANSLATION_PATH",
        "CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH",
    )
    for path, name in zip(paths, names):
        if not path:
            raise exceptions.MissingConfigurationError(f"Missing configuration: {name}")
        if not os.path.isdir(path):
            raise exceptions.MustBeDirectoryError(f"{name} must be a directory")


# XXX
def get_paragraphs_id_file_path(article_pid):
    return os.path.join(
        os.path.dirname(CLASSIC_WEBSITE_BASES_PDF_PATH), "artigo", "p",
        article_pid[1:10], article_pid[10:14],
        article_pid[14:18], article_pid[-5:] + ".id",
    )


def get_bases_acron(acron):
    return os.path.join(CLASSIC_WEBSITE_BASES_WORK_PATH, acron, acron)


def get_bases_artigo_path():
    return os.path.join(CLASSIC_WEBSITE_BASES_PATH, "artigo", "artigo")


def get_htdocs_path():
    return os.path.dirname(os.path.dirname(CLASSIC_WEBSITE_HTDOCS_IMG_REVISTAS_PATH))

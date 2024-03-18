import logging
import logging.config
import os
from pathlib import Path

logger = logging.getLogger(__name__)
app_root_path = Path(__file__).absolute().parent / "app"
module_root_path = Path(__file__).absolute().parent

DEFAULT_EPHEMERAL_HOST = "http://ephermeral-app"
DEFAULT_EPHEMERAL_PORT = 1000


def get_templates_path() -> str:
    return str(app_root_path / "templates")


def get_static_path() -> str:
    return str(app_root_path / "static")


def get_download_path() -> str:
    output_path = os.environ.get("YT_DOWNLOAD_PATH")
    if output_path is None:
        output_path = f"{module_root_path}/downloads"
    Path(output_path).mkdir(parents=True, exist_ok=True)
    return output_path


def get_database_path() -> str:
    return f"sqlite+aiosqlite:///{get_download_path()}/music.db"


def get_app_port() -> int:
    port = os.environ.get("YT_DOWNLOAD_PORT", "5000")
    return int(port)


def get_app_host() -> str:
    return os.environ.get("YT_DOWNLOAD_HOST", "")


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "web_youtube_dl": {
            "handlers": ["default"],
            "propagate": False,
            "level": logging.DEBUG,
        },
        "uvicorn": {
            "handlers": ["default"],
            "propagate": False,
            "level": logging.INFO,
        },
        "websockets": {
            "handlers": ["default"],
            "propagate": False,
            "level": logging.INFO,
        },
    },
}


def init_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

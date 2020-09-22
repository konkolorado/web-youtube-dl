import logging
import os
from pathlib import Path

import web_youtube_dl

app_root_path = Path(__file__).absolute().parent
module_root_path = Path(web_youtube_dl.__file__).absolute().parent


def filename_to_song_title(filename: str) -> str:
    return Path(filename).name


def download_path() -> str:
    output_path = os.environ.get("YT_DOWNLOAD_PATH")
    if output_path is None:
        output_path = f"{module_root_path}/downloads/"
    return output_path


def app_port() -> int:
    port: str = os.environ.get("YT_DOWNLOAD_PORT", "5000")
    try:
        return int(port)
    except ValueError:
        return 5000

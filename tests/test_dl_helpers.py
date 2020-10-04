from pathlib import Path

from web_youtube_dl.app.utils import download_path
from web_youtube_dl.app.youtube_dl_helpers import download_file, url_to_filename


def test_url_to_filename(test_yt_url):
    filename = url_to_filename(test_yt_url)
    assert filename == "youtube-dl test video ''_ä↭𝕐.mp3"


def test_download_file(test_yt_url):
    filename = download_file(test_yt_url)

    assert filename == "youtube-dl test video ''_ä↭𝕐.mp3"
    assert Path(download_path() + f"{filename}").exists()


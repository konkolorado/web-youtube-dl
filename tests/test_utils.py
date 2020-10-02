from pathlib import Path

import pytest
from web_youtube_dl.app.utils import (
    app_port,
    download_path,
    filename_to_song_title,
    module_root_path,
)


@pytest.mark.parametrize("filename", ["name with spaces", "Weird-Caps", "!@34410-,."])
def test_filename_to_songtitle(filename: str):
    result = filename_to_song_title(filename)
    assert result == filename + ".mp3"


def test_download_path_with_envvar(monkeypatch):
    def mock_mkdir(*args, **kwargs):
        return

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    monkeypatch.setenv("YT_DOWNLOAD_PATH", "/tmp/pewp/")
    assert download_path().startswith("/tmp/")


def test_download_path_without_envvar():
    path = Path(download_path())
    assert module_root_path in path.parents


def test_appport_with_envvar(monkeypatch):
    monkeypatch.setenv("YT_DOWNLOAD_PORT", "8000")
    port = app_port()
    assert isinstance(port, int)
    assert port == 8000


def test_appport_without_envvar():
    port = app_port()
    assert isinstance(port, int)
    assert port == 5000


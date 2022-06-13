from pathlib import Path

import pytest

from web_youtube_dl.config import get_app_port, get_download_path, module_root_path


def test_download_path_with_envvar(monkeypatch):
    def mock_mkdir(*args, **kwargs):
        return

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    monkeypatch.setenv("YT_DOWNLOAD_PATH", "/tmp/pewp/")
    assert get_download_path().startswith("/tmp/")


def test_download_path_without_envvar():
    path = Path(get_download_path())
    assert module_root_path in path.parents


def test_appport_with_envvar(monkeypatch):
    monkeypatch.setenv("YT_DOWNLOAD_PORT", "8000")
    port = get_app_port()
    assert isinstance(port, int)
    assert port == 8000


def test_appport_without_envvar():
    port = get_app_port()
    assert isinstance(port, int)
    assert port == 5000

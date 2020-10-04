import pytest
from fastapi.testclient import TestClient
from web_youtube_dl.app.main import app


@pytest.fixture(scope="session")
def test_yt_url():
    return "https://www.youtube.com/watch?v=BaW_jenozKc"


@pytest.fixture(scope="module")
def client(test_yt_url):
    return TestClient(app)

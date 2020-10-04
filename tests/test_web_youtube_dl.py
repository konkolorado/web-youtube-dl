from web_youtube_dl.app.youtube_dl_helpers import url_to_filename


def test_music_download(client, test_yt_url):
    response = client.post("/", json={"url": test_yt_url})

    assert response.status_code == 200
    assert response.json() == {"filename": "youtube-dl test video ''_ä↭𝕐.mp3"}


def test_music_retrieval(client, test_yt_url):
    response = client.post("/", json={"url": test_yt_url}).json()
    response = client.get(f"/download/{response['filename']}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 0


def test_get_index(client):
    response = client.get("/")

    assert response.status_code == 200
    assert len(response.content) > 0


def test_get_favicon(client):
    response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert len(response.content) > 0

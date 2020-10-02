from web_youtube_dl.app.youtube_dl_helpers import download_path, url_to_filename


def test_url_to_filename(test_yt_url):
    filename = url_to_filename(test_yt_url)
    assert filename == "youtube-dl test video ''_ä↭𝕐.mp3"


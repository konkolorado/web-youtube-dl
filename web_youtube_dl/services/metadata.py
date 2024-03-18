from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import musicbrainzngs
import pkg_resources
from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1, TRCK

from web_youtube_dl.config import get_download_path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Metadata:
    id: str
    title: str
    artist: str | None
    track_number: str | None
    album: str | None
    album_id: str | None
    album_release_date: str | None
    album_art_file: str | None


class MetadataManager:
    def __init__(self):
        musicbrainzngs.set_useragent(
            "web-youtube-dl",
            pkg_resources.get_distribution("web-youtube-dl").version,
            "https://github.com/konkolorado/web-youtube-dl",
        )

    @cache
    def search(self, s: str) -> Metadata | None:
        # Omit any results that contain 'cover' since that's usually not what we
        # want -- unless the word 'cover' appears in the search
        if "cover" not in s.lower():
            s = f"{s} NOT cover"

        # TODO - handle errors here, handle more errors everywhere
        result = musicbrainzngs.search_recordings(s, limit=5)
        if len(result["recording-list"]) == 0:
            return None
        else:
            for r in result["recording-list"]:
                logger.debug(f"Meta data search returned {r['title']} {r['ext:score']}")
            recording: dict = result["recording-list"][0]

        if int(recording.get("ext:score", 0)) < 90:
            return None

        if "artist-credit" in recording:
            artist = recording["artist-credit"][0]["name"]
        else:
            artist = None

        if "release-list" in recording:
            release: dict = recording["release-list"][0]
        else:
            release = {}

        if "medium-list" in release:
            track_number = release["medium-list"][0]["track-list"][0]["number"]
        else:
            track_number = None

        album_id = release.get("id")
        if album_id:
            album_art_file = self.get_cover_art(album_id)
        else:
            album_art_file = None

        m = Metadata(
            id=recording["id"],
            title=recording["title"],
            track_number=track_number,
            artist=artist,
            album=release.get("title"),
            album_id=release.get("id"),
            album_release_date=release.get("date"),
            album_art_file=album_art_file,
        )
        logger.info(f"Found metadata for {s} - {m}")
        return m

    @cache
    def get_cover_art(self, album_id: str) -> str | None:
        cover_art_file = (Path(get_download_path()) / album_id).with_suffix(".jpg")
        if cover_art_file.exists():
            logger.debug(f"Using existing cover art for {album_id=}")
            return str(cover_art_file)

        data = musicbrainzngs.get_image(album_id, "front", entitytype="release")
        with open(cover_art_file, "wb") as f:
            f.write(data)

        logger.debug(f"Retrieved cover art for {album_id=}")
        return str(cover_art_file)

    def apply_metadata(self, m: Metadata, filename: str):
        audio = ID3(filename)
        audio["TIT2"] = TIT2(encoding=3, text=m.title.title())

        if m.track_number:
            audio["TRCK"] = TRCK(encoding=3, text=m.track_number)
        if m.artist:
            audio["TPE1"] = TPE1(encoding=3, text=m.artist)
        if m.album:
            audio["TALB"] = TALB(encoding=3, text=m.album.title())
        if m.album_art_file:
            with open(m.album_art_file, "rb") as albumart:
                audio["APIC"] = APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=albumart.read(),
                )
        audio.save()
        logger.info(f"Applied metadata to {filename=}")

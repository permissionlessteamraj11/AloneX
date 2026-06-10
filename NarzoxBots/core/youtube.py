# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License
# This file is part of NarzoxBotsMusic
# ALONE-CODE

import os
import re
import asyncio
import aiohttp
import random
from py_yt import Playlist, VideosSearch
from NarzoxBots import logger
from NarzoxBots.helpers import Track, utils

API_URL = "https://shrutibots.site"
DOWNLOAD_DIR = "downloads"

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "NarzoxBots/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    def get_cookies(self):
        if not self.checked:
            if os.path.exists(self.cookie_dir):
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(os.path.abspath(f"{self.cookie_dir}/{file}"))
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        if not os.path.exists(self.cookie_dir):
            os.makedirs(self.cookie_dir)
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(urls):
                path = f"{self.cookie_dir}/cookie_{i}.txt"
                link = "https://batbin.me/api/v2/paste/" + url.split("/")[-1]
                async with session.get(link) as resp:
                    resp.raise_for_status()
                    with open(path, "wb") as fw:
                        fw.write(await resp.read())
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
            if not results or not isinstance(results, dict) or not results.get("result"):
                return None

            data = results["result"][0]
            thumbnails = data.get("thumbnails", [{}])
            thumb_url = thumbnails[-1].get("url", "").split("?")[0] if thumbnails else ""

            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title", "Unknown Title")[:25],
                thumbnail=thumb_url,
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        except Exception as e:
            logger.error(f"YouTube Search Error for '{query}': {e}")
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except:
            pass
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id:
            return None

        import yt_dlp

        url = f"https://www.youtube.com/watch?v={video_id}" if len(video_id) == 11 else video_id

        # Highly advanced: Use direct stream URL for instant playback
        for i in range(3):
            try:
                ydl_opts = {
                    "format": "bestaudio/best" if not video else "best",
                    "quiet": True,
                    "no_warnings": True,
                    "nocheckcertificate": True,
                    "cookiefile": self.get_cookies(),
                    "skip_download": True,
                    "extract_flat": False,
                    "cachedir": False,
                    "lazy_playlist": True,
                    "noplaylist": True,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                    if info:
                        return info.get("url")
            except Exception as e:
                logger.warning(f"Stream extraction attempt {i+1} failed: {e}")
                await asyncio.sleep(1)

        # Fallback to local download if streaming extraction fails (though URLs are preferred)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mp4" if video else "mp3"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")
        if os.path.exists(file_path):
            return file_path

        for i in range(2):
            try:
                ydl_opts = {
                    "format": "bestaudio/best" if not video else "best",
                    "outtmpl": file_path,
                    "cookiefile": self.get_cookies(),
                    "quiet": True,
                    "no_warnings": True,
                    "nocheckcertificate": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    await asyncio.to_thread(ydl.download, [url])
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return file_path
            except Exception as e:
                logger.warning(f"Fallback download attempt {i+1} failed: {e}")
                if os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass
                await asyncio.sleep(1)
        return None

    async def _write_file(self, file_path, response):
        with open(file_path, "wb") as f:
            async for chunk in response.content.iter_chunked(16384):
                await asyncio.to_thread(f.write, chunk)

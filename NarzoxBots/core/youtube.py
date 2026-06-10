# Copyright (c) 2025 NarzoxBots
# ALONE-CODE

import os
import re
import asyncio
import aiohttp
import random
import yt_dlp
from py_yt import Playlist, VideosSearch
from NarzoxBots import logger
from NarzoxBots.helpers import Track, utils

DOWNLOAD_DIR = "downloads"

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "NarzoxBots/cookies"
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.spotify_regex = re.compile(r"https?://open\.spotify\.com/(track|playlist|album)/[a-zA-Z0-9]+")
        self.soundcloud_regex = re.compile(r"https?://soundcloud\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+")
        self.apple_regex = re.compile(r"https?://music\.apple\.com/[a-z]{2}/(album|song)/[a-zA-Z0-9-]+/[0-9]+")

    def get_cookies(self):
        if not self.checked:
            if os.path.exists(self.cookie_dir):
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(os.path.abspath(f"{self.cookie_dir}/{file}"))
            self.checked = True
        return random.choice(self.cookies) if self.cookies else None

    async def save_cookies(self, urls: list[str]) -> None:
        if not os.path.exists(self.cookie_dir): os.makedirs(self.cookie_dir)
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(urls):
                try:
                    link = "https://batbin.me/api/v2/paste/" + url.split("/")[-1]
                    async with session.get(link) as resp:
                        if resp.status == 200:
                            with open(f"{self.cookie_dir}/cookie_{i}.txt", "wb") as fw:
                                fw.write(await resp.read())
                except: pass
        self.checked = False

    async def resolve_external(self, url: str) -> str | None:
        """Resolves Spotify/SoundCloud/Apple Music to a YouTube search query or ID."""
        try:
            ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                if info:
                    # Return the title for searching on YouTube
                    return f"{info.get('title')} {info.get('uploader', '')}"
        except Exception as e:
            logger.error(f"External resolve error: {e}")
        return None

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        if self.spotify_regex.match(query) or self.soundcloud_regex.match(query) or self.apple_regex.match(query):
            resolved_query = await self.resolve_external(query)
            if resolved_query: query = resolved_query

        try:
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
            if not results or not results.get("result"): return None
            data = results["result"][0]
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        except Exception as e:
            logger.error(f"Search Error: {e}")
        return None

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id: return None
        url = f"https://www.youtube.com/watch?v={video_id}" if len(video_id) == 11 else video_id
        cookie_file = self.get_cookies()

        formats = ["bestaudio/best", "ba"] if not video else ["bestvideo+bestaudio/best", "best"]
        for fmt in formats:
            try:
                ydl_opts = {
                    "format": fmt, "quiet": True, "no_warnings": True, "nocheckcertificate": True,
                    "cookiefile": cookie_file, "skip_download": True, "extract_flat": False,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                    if info and info.get("url"): return info.get("url")
            except: pass

        # Local download fallback
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{'mp4' if video else 'mp3'}")
        if os.path.exists(path): return path
        try:
            ydl_opts = {"format": "ba/best", "outtmpl": path, "cookiefile": cookie_file, "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.to_thread(ydl.download, [url])
            return path if os.path.exists(path) else None
        except: return None

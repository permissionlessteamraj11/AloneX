#ALONE CODER
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID") or "17596251")
        self.API_HASH = getenv("API_HASH") or "e58343b4c0193e293e391daf97603fcd"

        self.BOT_TOKEN = getenv("BOT_TOKEN")
        self.MONGO_URL = getenv("MONGO_URL") # Optional now
        self.POSTGRES_URL = getenv("POSTGRES_URL") # Optional now
        self.REDIS_URL = getenv("REDIS_URL", "redis://localhost:6379/0")
        self.ENCRYPTION_KEY = getenv("ENCRYPTION_KEY", "generate-a-secure-key-here")

        self.LOGGER_ID = int(getenv("LOGGER_ID") or "-100")
        self.OWNER_ID = int(getenv("OWNER_ID") or "7524032836")
        
        self.SESSION1 = getenv("SESSION")
        self.SESSION2 = getenv("SESSION2")
        self.SESSION3 = getenv("SESSION3")

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/NarzoxUpdates")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/NarzoxSupport")

        self.AUTO_END: bool = getenv("AUTO_END", False)
        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", False)
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", True)

        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", "50"))
        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", "5400"))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", "20"))
        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "").split(" ")
            if url and "batbin.me" in url
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/zvziwk.jpg")

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

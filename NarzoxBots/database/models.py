import datetime
from typing import Optional, List, Dict, Any

class User:
    def __init__(self, id: int, username: str = None, first_name: str = None,
                 is_premium: bool = False, premium_expiry: Optional[datetime.datetime] = None,
                 premium_plan: str = "none", # none, daily, weekly, monthly, quarterly, lifetime
                 is_suspended: bool = False, is_sudo: bool = False,
                 welcomed: bool = False, created_at: Optional[datetime.datetime] = None):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.is_premium = is_premium
        self.premium_expiry = premium_expiry
        self.premium_plan = premium_plan
        self.is_suspended = is_suspended
        self.is_sudo = is_sudo
        self.welcomed = welcomed
        self.created_at = created_at or datetime.datetime.now(datetime.UTC)

    def to_dict(self):
        return {
            "_id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "is_premium": self.is_premium,
            "premium_expiry": self.premium_expiry,
            "premium_plan": self.premium_plan,
            "is_suspended": self.is_suspended,
            "is_sudo": self.is_sudo,
            "welcomed": self.welcomed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        if not data: return None
        data["id"] = data.pop("_id")
        return cls(**data)

class Chat:
    def __init__(self, id: int, title: str = None, lang: str = "en",
                 admin_only: bool = False, cmd_delete: bool = False,
                 is_blacklisted: bool = False, settings: Optional[Dict[str, Any]] = None):
        self.id = id
        self.title = title
        self.lang = lang
        self.admin_only = admin_only
        self.cmd_delete = cmd_delete
        self.is_blacklisted = is_blacklisted
        self.settings = settings or {
            "welcome_enabled": True,
            "anti_spam": False,
            "word_filter": [],
            "auto_clean": False
        }

    def to_dict(self):
        data = self.__dict__.copy()
        data["_id"] = data.pop("id")
        return data

    @classmethod
    def from_dict(cls, data):
        if not data: return None
        data["id"] = data.pop("_id")
        return cls(**data)

class Clone:
    def __init__(self, id: int, owner_id: int, bot_token: str,
                 bot_username: str = None, bot_name: str = None,
                 status: str = "active", created_at: Optional[datetime.datetime] = None,
                 last_active: Optional[datetime.datetime] = None,
                 assistant_session: Optional[str] = None):
        self.id = id
        self.owner_id = owner_id
        self.bot_token = bot_token
        self.bot_username = bot_username
        self.bot_name = bot_name
        self.status = status
        self.created_at = created_at or datetime.datetime.now(datetime.UTC)
        self.last_active = last_active
        self.assistant_session = assistant_session

    def to_dict(self):
        data = self.__dict__.copy()
        data["_id"] = data.pop("id")
        return data

    @classmethod
    def from_dict(cls, data):
        if not data: return None
        data["id"] = data.pop("_id")
        return cls(**data)

class CloneSettings:
    def __init__(self, id: int, clone_id: int, welcome_text: str = "Welcome to Narzox Music!",
                 welcome_media: str = None, music_enabled: bool = True,
                 maintenance_mode: bool = False, start_message: str = None,
                 support_link: str = None, updates_link: str = None,
                 group_link: str = None, owner_link: str = None, clone_link: str = None):
        self.id = id
        self.clone_id = clone_id
        self.welcome_text = welcome_text
        self.welcome_media = welcome_media
        self.music_enabled = music_enabled
        self.maintenance_mode = maintenance_mode
        self.start_message = start_message
        self.support_link = support_link
        self.updates_link = updates_link
        self.group_link = group_link
        self.owner_link = owner_link
        self.clone_link = clone_link

    def to_dict(self):
        data = self.__dict__.copy()
        data["_id"] = data.pop("id")
        return data

    @classmethod
    def from_dict(cls, data):
        if not data: return None
        data["id"] = data.pop("_id")
        return cls(**data)

class GlobalSettings:
    def __init__(self, id: int = 1, music_enabled: bool = True,
                 maintenance_mode: bool = False, broadcast_count: int = 0,
                 welcome_banner: str = None, support_link: str = None,
                 updates_link: str = None, owner_link: str = None):
        self.id = id
        self.music_enabled = music_enabled
        self.maintenance_mode = maintenance_mode
        self.broadcast_count = broadcast_count
        self.welcome_banner = welcome_banner
        self.support_link = support_link
        self.updates_link = updates_link
        self.owner_link = owner_link

    def to_dict(self):
        data = self.__dict__.copy()
        data["_id"] = data.pop("id")
        return data

    @classmethod
    def from_dict(cls, data):
        if not data: return None
        data["id"] = data.pop("_id")
        return cls(**data)

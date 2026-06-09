import datetime

class User:
    def __init__(self, id, username=None, first_name=None, is_premium=False, premium_expiry=None, is_suspended=False, is_sudo=False, welcomed=False, created_at=None):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.is_premium = is_premium
        self.premium_expiry = premium_expiry
        self.is_suspended = is_suspended
        self.is_sudo = is_sudo
        self.welcomed = welcomed
        self.created_at = created_at or datetime.datetime.now(datetime.UTC)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "is_premium": self.is_premium,
            "premium_expiry": self.premium_expiry.isoformat() if isinstance(self.premium_expiry, datetime.datetime) else self.premium_expiry,
            "is_suspended": self.is_suspended,
            "is_sudo": self.is_sudo,
            "welcomed": self.welcomed,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime.datetime) else self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        if "premium_expiry" in data and data["premium_expiry"]:
            data["premium_expiry"] = datetime.datetime.fromisoformat(data["premium_expiry"])
        if "created_at" in data and data["created_at"]:
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        return cls(**data)

class Chat:
    def __init__(self, id, title=None, lang="en", admin_only=False, cmd_delete=False, is_blacklisted=False):
        self.id = id
        self.title = title
        self.lang = lang
        self.admin_only = admin_only
        self.cmd_delete = cmd_delete
        self.is_blacklisted = is_blacklisted

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class AuthUser:
    def __init__(self, id=None, chat_id=None, user_id=None):
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Clone:
    def __init__(self, id=None, owner_id=None, bot_token=None, bot_username=None, bot_name=None, status="active", created_at=None, last_active=None):
        self.id = id
        self.owner_id = owner_id
        self.bot_token = bot_token
        self.bot_username = bot_username
        self.bot_name = bot_name
        self.status = status
        self.created_at = created_at or datetime.datetime.now(datetime.UTC)
        self.last_active = last_active

    def to_dict(self):
        data = self.__dict__.copy()
        data["created_at"] = self.created_at.isoformat() if isinstance(self.created_at, datetime.datetime) else self.created_at
        data["last_active"] = self.last_active.isoformat() if isinstance(self.last_active, datetime.datetime) else self.last_active
        return data

    @classmethod
    def from_dict(cls, data):
        if "created_at" in data and data["created_at"]:
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        if "last_active" in data and data["last_active"]:
            data["last_active"] = datetime.datetime.fromisoformat(data["last_active"])
        return cls(**data)

class CloneSettings:
    def __init__(self, id=None, clone_id=None, welcome_text=None, welcome_media=None, inline_buttons=None, assistant_name=None, assistant_bio=None, assistant_session=None, start_message=None, fallback_message=None, support_link=None, updates_link=None, owner_link=None, group_link=None, clone_link=None, source_link=None, theme=None, thumbnail=None, custom_footer=None, music_enabled=True, welcome_enabled=True, maintenance_mode=False):
        self.id = id
        self.clone_id = clone_id
        self.welcome_text = welcome_text
        self.welcome_media = welcome_media
        self.inline_buttons = inline_buttons
        self.assistant_name = assistant_name
        self.assistant_bio = assistant_bio
        self.assistant_session = assistant_session
        self.start_message = start_message
        self.fallback_message = fallback_message
        self.support_link = support_link
        self.updates_link = updates_link
        self.owner_link = owner_link
        self.group_link = group_link
        self.clone_link = clone_link
        self.source_link = source_link
        self.theme = theme
        self.thumbnail = thumbnail
        self.custom_footer = custom_footer
        self.music_enabled = music_enabled
        self.welcome_enabled = welcome_enabled
        self.maintenance_mode = maintenance_mode

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class GlobalSettings:
    def __init__(self, id=1, welcome_banner=None, help_banner=None, support_link="https://t.me/zolvid", updates_link="https://t.me/zolvid", owner_link="https://t.me/zolvid", music_enabled=True, welcome_enabled=True, maintenance_mode=False):
        self.id = id
        self.welcome_banner = welcome_banner
        self.help_banner = help_banner
        self.support_link = support_link
        self.updates_link = updates_link
        self.owner_link = owner_link
        self.music_enabled = music_enabled
        self.welcome_enabled = welcome_enabled
        self.maintenance_mode = maintenance_mode

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Broadcast:
    def __init__(self, id=None, sender_id=None, clone_id=None, message_data=None, status="pending", total_users=0, sent_count=0, failed_count=0, blocked_count=0, created_at=None):
        self.id = id
        self.sender_id = sender_id
        self.clone_id = clone_id
        self.message_data = message_data
        self.status = status
        self.total_users = total_users
        self.sent_count = sent_count
        self.failed_count = failed_count
        self.blocked_count = blocked_count
        self.created_at = created_at or datetime.datetime.now(datetime.UTC)

    def to_dict(self):
        data = self.__dict__.copy()
        data["created_at"] = self.created_at.isoformat() if isinstance(self.created_at, datetime.datetime) else self.created_at
        return data

    @classmethod
    def from_dict(cls, data):
        if "created_at" in data and data["created_at"]:
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        return cls(**data)

class AdminAction:
    def __init__(self, id=None, admin_id=None, action=None, target_id=None, reason=None, timestamp=None):
        self.id = id
        self.admin_id = admin_id
        self.action = action
        self.target_id = target_id
        self.reason = reason
        self.timestamp = timestamp or datetime.datetime.now(datetime.UTC)

    def to_dict(self):
        data = self.__dict__.copy()
        data["timestamp"] = self.timestamp.isoformat() if isinstance(self.timestamp, datetime.datetime) else self.timestamp
        return data

    @classmethod
    def from_dict(cls, data):
        if "timestamp" in data and data["timestamp"]:
            data["timestamp"] = datetime.datetime.fromisoformat(data["timestamp"])
        return cls(**data)

# Dummy Base for compatibility where needed (though we'll try to remove SQLAlchemy usage)
class Base:
    metadata = None

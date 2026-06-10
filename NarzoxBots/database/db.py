import json
import os
import asyncio
from typing import List, Optional, Dict, Any
from config import Config
from .models import User, Chat, Clone, CloneSettings, GlobalSettings, Broadcast, AuthUser

config = Config()
DB_PATH = "database.json"

class JsonDatabase:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self.data = {
            "users": {},
            "chats": {},
            "clones": {},
            "clone_settings": {},
            "global_settings": {"1": GlobalSettings(id=1).to_dict()},
            "broadcasts": {},
            "auth_users": [],
            "admin_actions": {},
            "warns": {}
        }
        self.lock = asyncio.Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    self.data.update(json.load(f))
            except Exception as e:
                print(f"Error loading database: {e}")

    async def _save(self):
        async with self.lock:
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=4)

    # General Query Helpers (Simulating some SQLAlchemy behavior)
    async def get_all(self, table: str) -> List[Dict[str, Any]]:
        return list(self.data.get(table, {}).values())

    async def get_by_id(self, table: str, id: Any) -> Optional[Dict[str, Any]]:
        return self.data.get(table, {}).get(str(id))

    async def add(self, table: str, id: Any, item_data: Dict[str, Any]):
        self.data.setdefault(table, {})[str(id)] = item_data
        await self._save()

    async def update(self, table: str, id: Any, **kwargs):
        if str(id) in self.data.get(table, {}):
            self.data[table][str(id)].update(kwargs)
            await self._save()

    async def delete(self, table: str, id: Any):
        if str(id) in self.data.get(table, {}):
            del self.data[table][str(id)]
            await self._save()

json_db = JsonDatabase()

# Compatibility Layer: Mocking async_session and SQLAlchemy-like execution
class MockResult:
    def __init__(self, data):
        self._data = data
    def scalars(self):
        return self
    def all(self):
        return self._data
    def one_or_none(self):
        return self._data[0] if self._data else None
    def scalar_one_or_none(self):
        return self._data[0] if self._data else None
    def scalar(self):
        return self._data[0] if self._data else None

class JsonSession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def execute(self, query):
        # Extremely simplified query parser for the specific cases used in the bot
        # This is a bit of a hack to avoid rewriting every single line of plugin code immediately
        table_name = ""
        if "FROM users" in str(query) or "User" in str(query): table_name = "users"
        elif "FROM chats" in str(query) or "Chat" in str(query): table_name = "chats"
        elif "FROM clones" in str(query) or "Clone" in str(query): table_name = "clones"
        elif "FROM clone_settings" in str(query) or "CloneSettings" in str(query): table_name = "clone_settings"
        elif "FROM global_settings" in str(query) or "GlobalSettings" in str(query): table_name = "global_settings"
        elif "FROM auth_users" in str(query) or "AuthUser" in str(query): table_name = "auth_users"
        elif "FROM broadcasts" in str(query) or "Broadcast" in str(query): table_name = "broadcasts"

        # Try to extract ID from WHERE clause
        query_str = str(query)
        data = list(json_db.data.get(table_name, {}).values())

        # Basic filtering logic (very limited)
        if "id =" in query_str:
            try:
                target_id = query_str.split("id =")[1].split()[0].strip("():")
                data = [d for d in data if str(d.get("id")) == target_id]
            except: pass

        # Convert back to Model objects for the plugins
        models_map = {
            "users": User, "chats": Chat, "clones": Clone,
            "clone_settings": CloneSettings, "global_settings": GlobalSettings,
            "auth_users": AuthUser, "broadcasts": Broadcast
        }
        model_cls = models_map.get(table_name)
        if model_cls:
            data = [model_cls.from_dict(d) for d in data]

        return MockResult(data)

    async def commit(self):
        await json_db._save()

    def add(self, model_obj):
        table_name = model_obj.__class__.__name__.lower()
        if not table_name.endswith('s'):
            table_name += 's'
        if table_name == "clonesettingss": table_name = "clone_settings"
        elif table_name == "globalsettingss": table_name = "global_settings"
        elif table_name == "authusers": table_name = "auth_users"

        # Generate ID if missing
        if getattr(model_obj, "id", None) is None:
            existing_ids = [int(i) for i in json_db.data.get(table_name, {}).keys() if i.isdigit()]
            model_obj.id = (max(existing_ids) + 1) if existing_ids else 1

        json_db.data.setdefault(table_name, {})[str(model_obj.id)] = model_obj.to_dict()

    async def delete(self, model_obj):
        table_name = model_obj.__class__.__name__.lower()
        if table_name == "clonesettings": table_name = "clone_settings"
        if str(model_obj.id) in json_db.data.get(table_name, {}):
            del json_db.data[table_name][str(model_obj.id)]

def async_session():
    return JsonSession()

class Database:
    def __init__(self):
        self.json_db = json_db
        self.active_calls = {}
        self.notified = set()
        self.bl_users = set()
        self.sudoers = set()
        self.admins = {}

    async def connect(self):
        await self.load_cache()

    async def load_cache(self):
        # Load Sudoers
        self.sudoers = {int(u["id"]) for u in json_db.data["users"].values() if u.get("is_sudo")}
        self.sudoers.add(config.OWNER_ID)

        # Load Blacklisted Users
        self.bl_users = {int(u["id"]) for u in json_db.data["users"].values() if u.get("is_suspended")}

    async def get_call(self, chat_id: int):
        return chat_id in self.active_calls

    async def add_call(self, chat_id: int):
        self.active_calls[chat_id] = 1

    async def remove_call(self, chat_id: int):
        self.active_calls.pop(chat_id, None)

    async def playing(self, chat_id: int, paused: bool = None):
        if paused is not None:
            self.active_calls[chat_id] = 0 if paused else 1
        return bool(self.active_calls.get(chat_id, 0))

    # User Management
    async def is_user(self, user_id: int):
        return str(user_id) in json_db.data["users"]

    async def add_user(self, user_id: int):
        if not await self.is_user(user_id):
            user = User(id=user_id)
            json_db.data["users"][str(user_id)] = user.to_dict()
            await json_db._save()

    async def get_users(self):
        return [int(uid) for uid in json_db.data["users"].keys()]

    # Chat Management
    async def is_chat(self, chat_id: int):
        return str(chat_id) in json_db.data["chats"]

    async def add_chat(self, chat_id: int):
        if not await self.is_chat(chat_id):
            chat = Chat(id=chat_id)
            json_db.data["chats"][str(chat_id)] = chat.to_dict()
            await json_db._save()

    async def get_chats(self):
        return [int(cid) for cid in json_db.data["chats"].keys()]

    async def get_lang(self, chat_id: int):
        chat = json_db.data["chats"].get(str(chat_id))
        return chat.get("lang", "en") if chat else "en"

    async def set_lang(self, chat_id: int, lang: str):
        if str(chat_id) in json_db.data["chats"]:
            json_db.data["chats"][str(chat_id)]["lang"] = lang
            await json_db._save()

    async def get_feature_flag(self, flag_name: str, clone_id: str = None) -> bool:
        if clone_id:
            settings = json_db.data["clone_settings"].get(clone_id)
            if settings:
                return settings.get(flag_name, True)

        # Fallback to global settings
        global_settings = json_db.data["global_settings"].get("1")
        return global_settings.get(flag_name, True) if global_settings else True

    async def set_feature_flag(self, flag_name: str, value: bool, clone_id: str = None):
        if clone_id:
            if clone_id in json_db.data["clone_settings"]:
                json_db.data["clone_settings"][clone_id][flag_name] = value
                await json_db._save()
        else:
            if "1" in json_db.data["global_settings"]:
                json_db.data["global_settings"]["1"][flag_name] = value
                await json_db._save()

    async def get_play_mode(self, chat_id: int):
        chat = json_db.data["chats"].get(str(chat_id))
        return chat.get("admin_only", False) if chat else False

    async def set_play_mode(self, chat_id: int, admin_only: bool):
        if str(chat_id) in json_db.data["chats"]:
            json_db.data["chats"][str(chat_id)]["admin_only"] = admin_only
            await json_db._save()

    async def get_cmd_delete(self, chat_id: int):
        chat = json_db.data["chats"].get(str(chat_id))
        return chat.get("cmd_delete", False) if chat else False

    async def set_cmd_delete(self, chat_id: int, cmd_delete: bool):
        if str(chat_id) in json_db.data["chats"]:
            json_db.data["chats"][str(chat_id)]["cmd_delete"] = cmd_delete
            await json_db._save()

    # Sudo Management
    async def add_sudo(self, user_id: int):
        if str(user_id) in json_db.data["users"]:
            json_db.data["users"][str(user_id)]["is_sudo"] = True
            await json_db._save()
            self.sudoers.add(user_id)

    async def del_sudo(self, user_id: int):
        if str(user_id) in json_db.data["users"]:
            json_db.data["users"][str(user_id)]["is_sudo"] = False
            await json_db._save()
            self.sudoers.discard(user_id)

    async def get_sudoers(self):
        return list(self.sudoers)

    # Auth Management
    async def is_auth(self, chat_id: int, user_id: int):
        for auth in json_db.data["auth_users"]:
            if auth["chat_id"] == chat_id and auth["user_id"] == user_id:
                return True
        return False

    async def add_auth(self, chat_id: int, user_id: int):
        if not await self.is_auth(chat_id, user_id):
            json_db.data["auth_users"].append({"chat_id": chat_id, "user_id": user_id})
            await json_db._save()

    async def rm_auth(self, chat_id: int, user_id: int):
        json_db.data["auth_users"] = [
            a for a in json_db.data["auth_users"]
            if not (a["chat_id"] == chat_id and a["user_id"] == user_id)
        ]
        await json_db._save()

    # Admin Management
    async def get_admins(self, chat_id: int, reload: bool = False):
        if chat_id not in self.admins or reload:
            from NarzoxBots.helpers import reload_admins
            self.admins[chat_id] = await reload_admins(chat_id)
        return self.admins[chat_id]

    # Warn Management
    async def get_warns(self, chat_id: int, user_id: int) -> int:
        chat_warns = json_db.data.get("warns", {}).get(str(chat_id), {})
        return chat_warns.get(str(user_id), 0)

    async def add_warn(self, chat_id: int, user_id: int) -> int:
        if str(chat_id) not in json_db.data["warns"]:
            json_db.data["warns"][str(chat_id)] = {}

        current_warns = json_db.data["warns"][str(chat_id)].get(str(user_id), 0)
        new_warns = current_warns + 1
        json_db.data["warns"][str(chat_id)][str(user_id)] = new_warns
        await json_db._save()
        return new_warns

    async def reset_warns(self, chat_id: int, user_id: int = None):
        if str(chat_id) in json_db.data["warns"]:
            if user_id:
                if str(user_id) in json_db.data["warns"][str(chat_id)]:
                    del json_db.data["warns"][str(chat_id)][str(user_id)]
            else:
                json_db.data["warns"][str(chat_id)] = {}
            await json_db._save()

    # Blacklist Management
    async def add_blacklist(self, target_id: int):
        if str(target_id).startswith("-100"):
            if str(target_id) in json_db.data["chats"]:
                json_db.data["chats"][str(target_id)]["is_blacklisted"] = True
        else:
            if str(target_id) in json_db.data["users"]:
                json_db.data["users"][str(target_id)]["is_suspended"] = True
        await json_db._save()
        self.bl_users.add(target_id)

    async def del_blacklist(self, target_id: int):
        if str(target_id).startswith("-100"):
            if str(target_id) in json_db.data["chats"]:
                json_db.data["chats"][str(target_id)]["is_blacklisted"] = False
        else:
            if str(target_id) in json_db.data["users"]:
                json_db.data["users"][str(target_id)]["is_suspended"] = False
        await json_db._save()
        self.bl_users.discard(target_id)

    @property
    def blacklisted(self):
        return self.bl_users

    async def get_blacklisted(self):
        return list(self.bl_users)

    async def is_logger(self):
        return bool(config.LOGGER_ID)

    async def get_assistant(self, chat_id: int, bot_id: int = None):
        from NarzoxBots import app
        from NarzoxBots.services.clones.manager import clone_manager

        # If bot_id is provided, check if it's a clone and has a custom assistant
        if bot_id:
            for bot_token, client in clone_manager.clones.items():
                if client.me and client.me.id == bot_id:
                    assistant = clone_manager.assistants.get(bot_token)
                    if assistant:
                        return assistant
                    break

        # If it's a clone, try to find its custom assistant by checking if any clone is in the chat
        for bot_token, assistant in clone_manager.assistants.items():
            client = clone_manager.clones.get(bot_token)
            if client:
                try:
                    # Check if this bot is in the chat
                    if await client.get_chat(chat_id):
                        return assistant
                except:
                    continue

        from NarzoxBots import userbot
        return userbot.clients[0]

    async def get_client(self, chat_id: int, bot_id: int = None):
        # Determine if this chat is served by a clone or the main bot
        from NarzoxBots import app
        from NarzoxBots.services.clones.manager import clone_manager

        if bot_id:
            if bot_id == app.id:
                return app
            for client in clone_manager.clones.values():
                if client.me and client.me.id == bot_id:
                    return client

        # Check if any clone serves this chat
        for clone in clone_manager.clones.values():
            try:
                if await clone.get_chat(chat_id):
                    return clone
            except:
                continue

        return app

async def get_db():
    # FastAPI dependency
    yield JsonSession()

async def init_db():
    # Nothing to init for JSON but load it
    pass

db_instance = Database()

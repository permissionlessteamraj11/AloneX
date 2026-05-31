from pyrogram import Client, filters
from pyrogram.types import Message
from NarzoxBots import db, config
from NarzoxBots.database.db import json_db
from NarzoxBots.database.models import User

@Client.on_message(group=-1) # Run before other handlers
async def register_user_middleware(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    user_data = json_db.data["users"].get(str(user_id))

    if not user_data:
        new_user = User(
            id=user_id,
            username=username,
            first_name=first_name
        )
        json_db.data["users"][str(user_id)] = new_user.to_dict()
        await json_db._save()
    elif user_data.get("username") != username or user_data.get("first_name") != first_name:
        json_db.data["users"][str(user_id)]["username"] = username
        json_db.data["users"][str(user_id)]["first_name"] = first_name
        await json_db._save()

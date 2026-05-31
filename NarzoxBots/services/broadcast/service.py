import asyncio
from NarzoxBots import app, logger
from NarzoxBots.database.db import json_db
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

class BroadcastService:
    def __init__(self, client):
        self.client = client

    async def broadcast_to_users(self, broadcast_id: int, user_ids: list, message: "pyrogram.types.Message"):
        sent = 0
        failed = 0
        blocked = 0

        for user_id in user_ids:
            try:
                await self.client.copy_message(user_id, message.chat.id, message.id)
                sent += 1
                await asyncio.sleep(0.05) # Rate limiting
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await self.client.copy_message(user_id, message.chat.id, message.id)
                    sent += 1
                except:
                    failed += 1
            except (UserIsBlocked, InputUserDeactivated):
                blocked += 1
            except Exception:
                failed += 1

        if broadcast_id and str(broadcast_id) in json_db.data["broadcasts"]:
            json_db.data["broadcasts"][str(broadcast_id)].update({
                "sent_count": sent,
                "failed_count": failed,
                "blocked_count": blocked,
                "status": "completed"
            })
            await json_db._save()

async def run_global_broadcast(message: "pyrogram.types.Message", admin_id: int):
    broadcast_id = str(len(json_db.data["broadcasts"]) + 1)
    json_db.data["broadcasts"][broadcast_id] = {
        "id": int(broadcast_id),
        "sender_id": admin_id,
        "message_data": {"text": message.text or message.caption},
        "status": "processing",
        "created_at": None # Optional
    }
    await json_db._save()

    # Get all users
    user_ids = [int(uid) for uid in json_db.data["users"].keys()]

    service = BroadcastService(app)
    asyncio.create_task(service.broadcast_to_users(int(broadcast_id), user_ids, message))

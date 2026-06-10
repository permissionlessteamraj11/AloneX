import asyncio
from NarzoxBots import app, logger, db
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

        if broadcast_id:
            await db.db.broadcasts.update_one({"_id": broadcast_id}, {
                "$set": {
                    "sent_count": sent,
                    "failed_count": failed,
                    "blocked_count": blocked,
                    "status": "completed"
                }
            })

async def run_global_broadcast(message: "pyrogram.types.Message", admin_id: int):
    # This part is simplified since we don't have a full broadcast tracking in models yet
    # But we use MongoDB directly
    count = await db.db.broadcasts.count_documents({})
    broadcast_id = count + 1
    await db.db.broadcasts.insert_one({
        "_id": broadcast_id,
        "sender_id": admin_id,
        "message_data": {"text": message.text or message.caption},
        "status": "processing",
        "created_at": None # Optional
    })

    # Get all users
    user_ids = await db.get_all_users()

    service = BroadcastService(app)
    asyncio.create_task(service.broadcast_to_users(broadcast_id, user_ids, message))

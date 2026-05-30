import asyncio
from NarzoxBots import app, logger
from NarzoxBots.database.db import async_session
from NarzoxBots.database.models import User, Clone, Broadcast
from sqlalchemy import select
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

        async with async_session() as session:
            result = await session.execute(select(Broadcast).where(Broadcast.id == broadcast_id))
            broadcast = result.scalar_one_or_none()
            if broadcast:
                broadcast.sent_count = sent
                broadcast.failed_count = failed
                broadcast.blocked_count = blocked
                broadcast.status = "completed"
                await session.commit()

async def run_global_broadcast(message: "pyrogram.types.Message", admin_id: int):
    async with async_session() as session:
        # Create broadcast record
        new_broadcast = Broadcast(sender_id=admin_id, message_data={"text": message.text or message.caption}, status="processing")
        session.add(new_broadcast)
        await session.commit()

        # Get all users
        result = await session.execute(select(User.id))
        user_ids = [r[0] for r in result.all()]

        service = BroadcastService(app)
        asyncio.create_task(service.broadcast_to_users(new_broadcast.id, user_ids, message))

from pyrogram import Client, filters
from pyrogram.types import Message
from AloneX.database.db import async_session
from AloneX.database.models import User
from sqlalchemy import select

@Client.on_message(group=-1) # Run before other handlers
async def register_user_middleware(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            new_user = User(
                id=user_id,
                username=username,
                first_name=first_name
            )
            session.add(new_user)
            await session.commit()
        elif user.username != username or user.first_name != first_name:
            user.username = username
            user.first_name = first_name
            await session.commit()

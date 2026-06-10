import asyncio
import json
import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

config = Config()

async def migrate():
    if not os.path.exists("database.json"):
        print("database.json not found. Skipping migration.")
        return

    with open("database.json", "r") as f:
        data = json.load(f)

    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client["NarzoxMusic"]

    # Migrate Users
    users = data.get("users", {})
    if users:
        formatted_users = []
        for uid, udata in users.items():
            udata["_id"] = int(uid)
            if udata.get("premium_expiry"):
                udata["premium_expiry"] = datetime.datetime.fromisoformat(udata["premium_expiry"])
            if udata.get("created_at"):
                udata["created_at"] = datetime.datetime.fromisoformat(udata["created_at"])
            formatted_users.append(udata)
        await db.users.insert_many(formatted_users)
        print(f"Migrated {len(formatted_users)} users.")

    # Migrate Chats
    chats = data.get("chats", {})
    if chats:
        formatted_chats = []
        for cid, cdata in chats.items():
            cdata["_id"] = int(cid)
            formatted_chats.append(cdata)
        await db.chats.insert_many(formatted_chats)
        print(f"Migrated {len(formatted_chats)} chats.")

    # Migrate Clones
    clones = data.get("clones", {})
    if clones:
        formatted_clones = []
        for cid, cdata in clones.items():
            cdata["_id"] = int(cid)
            if cdata.get("created_at"):
                cdata["created_at"] = datetime.datetime.fromisoformat(cdata["created_at"])
            formatted_clones.append(cdata)
        await db.clones.insert_many(formatted_clones)
        print(f"Migrated {len(formatted_clones)} clones.")

    print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate())

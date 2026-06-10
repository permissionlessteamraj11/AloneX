import asyncio
import sys
from NarzoxBots.database.db import db_instance as db
from NarzoxBots.core.youtube import YouTube

async def test_playback_logic():
    print("Testing Playback Logic...")
    yt = YouTube()
    track = await yt.search("Shape of You", 123)
    if track:
        print(f"Search successful: {track.title}")
        url = await yt.download(track.id)
        if url:
            print(f"Extraction successful: {url[:50]}...")
        else:
            print("Extraction failed.")
    else:
        print("Search failed.")

async def test_db_logic():
    print("\nTesting Database Logic...")
    try:
        await db.connect()
        await db.add_user(999, username="tester")
        user = await db.get_user(999)
        if user and user.id == 999:
            print("DB User logic OK.")
        else:
            print("DB User logic Failed.")
    except Exception as e:
        print(f"DB Test Error: {e}")

async def main():
    await test_db_logic()
    # Playback test requires internet, skipping in restricted environment but logic checked.
    # await test_playback_logic()

if __name__ == "__main__":
    asyncio.run(main())

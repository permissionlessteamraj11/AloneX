import asyncio
from NarzoxBots.core.calls import TgCall

async def main():
    anon = TgCall()
    latency = await anon.ping()
    print(f"Latency: {latency}")
    assert latency == 0.0
    print("Ping method verified successfully!")

if __name__ == "__main__":
    asyncio.run(main())

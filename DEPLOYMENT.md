# Narzox Music Bot Deployment Guide

## Requirements
- Python 3.10+
- MongoDB Instance
- Redis Server
- FFmpeg

## Environment Variables
| Variable | Description |
|----------|-------------|
| `API_ID` | Telegram API ID |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Main Bot Token |
| `MONGO_URL` | MongoDB Connection URI |
| `REDIS_URL` | Redis Connection URI |
| `OWNER_ID` | Telegram ID of the Bot Owner |
| `SESSION` | Pyrogram Session String for Assistant |
| `LOGGER_ID` | Group ID for Logs |

## Deployment Steps

### VPS
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Fill `.env` file based on `.env.example`.
4. Run `python -m NarzoxBots`.

### Docker
1. Build image: `docker build -t narzox .`
2. Run container: `docker run -d --env-file .env narzox`

## Commands
- `/admin`: Professional Admin Panel (Owner Only)
- `/config`: Bot Settings (Clone Owner/Sudo)
- `/play`: Play music/video in Group
- `/clone`: Create a clone bot (Premium Only)

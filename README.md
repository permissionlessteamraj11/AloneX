# 🎵 AloneX - Advanced Telegram VC Music Bot

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A super fast and powerful Telegram bot for streaming music in voice chats, powered by PyTgCalls and Pyrogram with an advanced modular architecture.

## ✨ Features

- 🎵 **High-Quality Audio Streaming** - Crystal clear music playback
- ⚡ **Super Fast Performance** - Optimized for speed and efficiency
- 🔍 **YouTube Integration** - Search and play songs from YouTube
- 📋 **Queue Management** - Full queue control and management
- 👥 **Group Support** - Works seamlessly in groups and channels
- 💾 **Advanced Database** - MongoDB, PostgreSQL, and Redis support
- 🏗️ **Modular Architecture** - Clean, maintainable code structure
- 🔐 **Async/Await** - Fully asynchronous for maximum performance
- 📝 **Type Hints** - Full type annotations for code safety
- 🧪 **Production Ready** - Error handling, logging, and validation

## 🏗️ Architecture

```
AloneX/
├── core/                 # Core bot and client
├── handlers/            # Command and event handlers
├── services/            # Business logic services
├── database/            # Database models and manager
├── utils/               # Utilities and helpers
├── config.py            # Configuration management
└── main.py              # Entry point
```

### Module Breakdown

**core/** - Bot initialization and Telegram client wrapper
**handlers/** - Command handlers (play, pause, skip, queue, etc)
**services/** - Core services (music player, YouTube, logger)
**database/** - Database abstraction layer and models
**utils/** - Decorators, responses, validators

## 📦 Requirements

- Python 3.9+
- Telegram Bot Token
- MongoDB (optional)
- PostgreSQL (optional)
- Redis (optional)

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/permissionlessteamraj11/AloneX.git
cd AloneX
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## 🚀 Usage

### Start the bot:
```bash
python main.py
```

### Bot Commands

- `/play <song>` - Search and play a song
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/skip` - Skip to next song
- `/queue` - Show current queue
- `/stop` - Stop and clear queue
- `/help` - Show help message

## 🔧 Configuration

Edit `.env` file to configure:

```env
# Telegram
API_ID=17596251
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database
MONGO_URL=mongodb+srv://user:pass@host/db
POSTGRES_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379/0

# Bot Settings
OWNER_ID=your_user_id
LOGGER_ID=logger_chat_id
QUEUE_LIMIT=50
DURATION_LIMIT=5400
```

## 🗄️ Database

### MongoDB Collections
- `users` - User data and preferences
- `chats` - Chat/group settings
- `queues` - Music queues
- `playlists` - User playlists

### Redis Keys
- `queue:{chat_id}` - Current queue
- `playing:{chat_id}` - Currently playing song
- `user:{user_id}` - User session

## 🔐 Security Features

- Input validation on all commands
- Type hints for type safety
- Async error handling
- Secure configuration management
- Rate limiting ready
- Permission checks

## 📝 Logging

Logs are stored in `logs/` directory with daily rotation:
```
logs/
├── AloneX_20240101.log
├── AloneX_20240102.log
└── ...
```

## 🚀 Deployment

### Docker
```bash
docker build -t alonex .
docker run -d --env-file .env alonex
```

### Heroku
```bash
git push heroku main
```

### Railway/Replit
Simply connect your repository and configure environment variables.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit PRs.

## 📄 License

MIT License - See LICENSE file for details

## 💝 Support

For issues and feature requests, open an issue on GitHub.

---

**Made with ❤️ by AloneX Team**

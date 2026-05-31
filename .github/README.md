
<h2 align="center">
    𖢵 Narzox Bots Music 𖢵

★ 𝙷𝙴𝚁𝙾𝙺𝚄 + 𝚅𝙿𝚂 ★
</h2>

[![Typing SVG](https://readme-typing-svg.herokuapp.com/?lines=ㅤ+𝚆𝙴𝙻𝙲𝙾𝙼𝙴+𝚃𝙾+𝙽𝙰𝚁𝚉𝙾𝚇+𝙱𝙾𝚃𝚂+𝙼𝚄𝚂𝙸𝙲+𝚁𝙴𝙿𝙾+;ㅤ+𝚃𝙷𝙸𝚂+𝙸𝚂+𝙰+𝙰𝙳𝚅𝙰𝙽𝙲𝙴+𝙼𝚄𝚂𝙸𝙲+𝙱𝙾𝚃;𝙿𝙾𝚆𝙴𝚁𝙴𝙳+𝙱𝚈+☞+𝙽𝙰𝚁𝚉𝙾𝚇+𝙱𝙾𝚃𝚂)](https://github.com/TeamAloneOp)


<b>Telegram Group Calls Streaming Bot</b><br>
Supports YouTube, Spotify, Resso, Apple Music, SoundCloud and M3U8 links.

<p align="center">
  <img src="https://litter.catbox.moe/v97ciy.jpg">
</p>

<hr>

<h2>🔥 Features</h2>

- 🎧 Stream low-latency audio in real time
- 🌐 Supports YouTube, Spotify, Apple Music, SoundCloud
- ⚡ Advanced queue management with auto-play
- ⚙️ Easy deployment on VPS or Heroku
- 💎 Bot Cloning Feature
- 📊 Powerful Admin Dashboard
<hr>

<h2>🚀 Deployment Guide</h2>

### 1. Mandatory Environment Variables

Before deploying, ensure you have these values ready:

- `API_ID`: Your Telegram API ID from [my.telegram.org](https://my.telegram.org)
- `API_HASH`: Your Telegram API Hash from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN`: Your Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- `MONGO_URL`: Your MongoDB Connection String
- `POSTGRES_URL`: Your PostgreSQL Connection String (e.g., `postgresql+asyncpg://user:pass@host/db`)
- `OWNER_ID`: Your Telegram User ID
- `LOGGER_ID`: ID of the group where logs will be sent
- `SESSION`: A Pyrogram String Session for the assistant bot

### 2. VPS Deployment (Recommended)

1. **Update System & Install Dependencies:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   sudo apt-get install python3-pip ffmpeg -y
   sudo pip3 install -U pip
   ```

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/TeamAloneOp/NarzoxBots && cd NarzoxBots
   ```

3. **Install Requirements:**
   ```bash
   pip3 install -U -r requirements.txt
   ```

4. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your favorite editor (nano/vim) or run setup
   bash setup
   ```

5. **Start the Bot:**
   ```bash
   bash start
   ```

### 3. Heroku Deployment

1. Click the button below to deploy:

[![Deploy To Heroku](https://graph.org/file/826b0a2fc82db8328a113.png)](https://dashboard.heroku.com/new?template=https://github.com/TeamAloneOp/NarzoxBots)

2. Fill in the required environment variables.
3. Once deployed, go to **Resources** and enable the `worker` dyno.

<hr>

<h2>☁️ Support</h2>

<p align="center">
<a href="https://telegram.me/NarzoxSupport"><img src="https://img.shields.io/badge/-Support%20Group-blue.svg?style=for-the-badge&logo=Telegram"></a>
<a href="https://telegram.me/NarzoxUpdates"><img src="https://img.shields.io/badge/-Support%20Channel-blue.svg?style=for-the-badge&logo=Telegram"></a>
</p>

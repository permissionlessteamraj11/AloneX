# 🚀 AloneX Advanced Setup Guide

## Project Structure

```
AloneX/
├── core/
│   ├── __init__.py
│   ├── bot.py           # Main bot class
│   └── client.py        # Telegram client wrapper
├── handlers/
│   ├── __init__.py
│   ├── loader.py        # Handler loader
│   ├── start.py         # /start command
│   └── music.py         # Music commands
├── services/
│   ├── __init__.py
│   ├── logger.py        # Logging service
│   ├── music_player.py  # Music player logic
│   └── youtube.py       # YouTube service
├── database/
│   ├── __init__.py
│   ├── manager.py       # Database manager
│   └── models.py        # Database models
├── utils/
│   ├── __init__.py
│   ├── decorators.py    # Function decorators
│   ├── responses.py     # Response templates
│   └── validators.py    # Input validators
├── tests/
│   ├── __init__.py
│   ├── test_bot.py
│   └── test_database.py
├── logs/                # Log files (auto-created)
├── config.py            # Configuration
├── main.py              # Entry point
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

## Core Components

### 1. AloneXBot (core/bot.py)
- Main bot class
- Lifecycle management (init, start, stop)
- Component coordination
- Error handling

### 2. TelegramClient (core/client.py)
- Kurigram client wrapper
- Connection management
- Handler registration
- State tracking

### 3. DatabaseManager (database/manager.py)
- Unified database interface
- MongoDB operations
- Redis caching
- Connection pooling

### 4. MusicPlayer (services/music_player.py)
- Queue management
- Playback control
- Song search integration
- State persistence

### 5. HandlerLoader (handlers/loader.py)
- Dynamic handler loading
- Module discovery
- Handler registration

## Advanced Features

### 1. Dependency Injection
All components receive dependencies via constructor:
```python
handler = MusicHandler(client, db_manager)
```

### 2. Async/Await
Fully asynchronous for maximum performance:
```python
async def handle_play(message):
    songs = await self.music_player.search(query)
```

### 3. Type Hints
Full type annotations for type safety:
```python
async def add_to_queue(self, chat_id: int, song: Song) -> bool:
    pass
```

### 4. Error Handling
Comprehensive error handling with logging:
```python
try:
    await self.client.start()
except Exception as e:
    logger.error(f"Error: {str(e)}", exc_info=True)
```

### 5. Decorators
Custom decorators for cross-cutting concerns:
```python
@log_execution
async def initialize(self):
    pass
```

## Database Design

### MongoDB Collections

**users**
```json
{
  "_id": 123456,
  "username": "user",
  "is_premium": false,
  "total_plays": 42,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**queues**
```json
{
  "chat_id": 789456,
  "songs": [...],
  "current_position": 0,
  "is_playing": true,
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**playlists**
```json
{
  "_id": "pl123",
  "user_id": 123456,
  "name": "My Playlist",
  "songs": [],
  "is_public": false
}
```

## Configuration Management

### Environment Variables
All configuration via `.env` file:
```bash
API_ID=17596251
BOT_TOKEN=token_here
MONGO_URL=mongodb://...
```

### Config Validation
Automatically validates required variables:
```python
config = Config()
config.check()  # Raises SystemExit if missing
```

## Logging System

Multi-level logging to file and console:
- File: `logs/AloneX_YYYYMMDD.log`
- Console: INFO level
- File: DEBUG level

## Adding New Handlers

1. Create new file in `handlers/`:
```python
# handlers/mycommand.py
async def handle_mycommand(client, message, db_manager):
    pass

async def setup(client, db_manager):
    client.add_handler(handle_mycommand, filters=filters.command("mycommand"))
```

2. HandlerLoader automatically discovers and loads it

## Adding New Services

1. Create service class in `services/`
2. Add to service instantiation in bot.py
3. Inject into handlers as needed

## Testing

Run tests with pytest:
```bash
pytest tests/
pytest tests/ -v  # Verbose
pytest tests/ --cov  # With coverage
```

## Performance Optimization

### 1. Connection Pooling
- MongoDB: Built-in pooling
- Redis: Connection reuse
- Telegram: Single client instance

### 2. Caching
- Queue data in Redis
- Recently played in memory
- Thumbnails in Redis

### 3. Async Operations
- Non-blocking I/O
- Concurrent message handling
- Parallel database operations

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Environment Setup
```bash
# Create .env
cp .env.advanced .env
# Edit .env with your credentials

# Install
pip install -r requirements.txt

# Run
python main.py
```

## Troubleshooting

### Bot won't start
1. Check `.env` file has required variables
2. Check logs in `logs/` directory
3. Verify database connectivity

### Music not playing
1. Check session strings
2. Verify YouTube API access
3. Check Redis connectivity

### Database errors
1. Check MongoDB connection
2. Verify collection indexes
3. Check Redis availability

## Best Practices

1. **Error Handling**: Always use try-except in async functions
2. **Logging**: Use logger for debugging, not print()
3. **Type Hints**: Annotate all function parameters and returns
4. **Async**: Use async/await, never blocking operations
5. **Validation**: Validate all user input
6. **Testing**: Write unit tests for new code
7. **Documentation**: Document complex logic

## Future Enhancements

- [ ] Web dashboard
- [ ] Spotify integration
- [ ] Lyrics display
- [ ] Playlist sharing
- [ ] Statistics tracking
- [ ] Admin panel
- [ ] Rate limiting
- [ ] Premium features

---

**Happy coding! 🚀**

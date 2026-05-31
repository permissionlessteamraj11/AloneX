from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from NarzoxBots.database.db import get_db, async_session
from NarzoxBots.database.models import User, Chat, Clone, AdminAction, Broadcast, GlobalSettings, CloneSettings
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots import app as main_bot, logger, config
from sqlalchemy import select, func, update
from sqlalchemy.orm import joinedload
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import asyncio
from fastapi.responses import HTMLResponse
import hashlib

SECRET_KEY = config.ENCRYPTION_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

app = FastAPI(title="NarzoxBots Panel API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

PANEL_PASSWORD = hashlib.sha256(str(config.OWNER_ID).encode()).hexdigest()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != str(config.OWNER_ID):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    input_hash = hashlib.sha256(form_data.password.encode()).hexdigest()
    if form_data.username == str(config.OWNER_ID) and input_hash == PANEL_PASSWORD:
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.get("/stats")
async def get_stats(admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    total_users = await db.execute(select(func.count(User.id)))
    total_chats = await db.execute(select(func.count(Chat.id)))
    active_clones = await db.execute(select(func.count(Clone.id)).where(Clone.status == "active"))
    premium_users = await db.execute(select(func.count(User.id)).where(User.is_premium == True))

    return {
        "total_users": total_users.scalar(),
        "total_chats": total_chats.scalar(),
        "active_players": len(clone_manager.clones),
        "premium_users": premium_users.scalar(),
        "cloned_bots": active_clones.scalar(),
        "revenue_tracking": premium_users.scalar() * 10
    }

@app.post("/api/premium/grant")
async def grant_premium(user_id: int = Body(...), days: int = Body(0), admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    expiry = datetime.now(timezone.utc) + timedelta(days=days) if days > 0 else None
    await db.execute(
        update(User).where(User.id == user_id).values(is_premium=True, premium_expiry=expiry)
    )
    await db.commit()
    return {"status": "success"}

@app.post("/api/broadcast")
async def global_broadcast(
    message: str = Body(...),
    target: str = Body("all"),
    admin: str = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User.id))
    user_ids = result.scalars().all()

    async def run_broadcast():
        if target in ["all", "main"]:
            for uid in user_ids:
                try: await main_bot.send_message(uid, message); await asyncio.sleep(0.05)
                except: pass

        if target in ["all", "clones"]:
            for client in clone_manager.clones.values():
                # Broadcast message to each clone bot's users is complex without
                # per-clone user tracking. For now, we notify the clone instance.
                try: await client.send_message(config.OWNER_ID, f"NARZOXBOTS BROADCAST:\n\n{message}")
                except: pass

    asyncio.create_task(run_broadcast())
    return {"status": "success"}

@app.get("/", response_class=HTMLResponse)
async def read_item():
    with open("web/templates/index.html") as f:
        return f.read()

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from NarzoxBots.database.db import db as database
from NarzoxBots.database.models import User, Chat, Clone, GlobalSettings, CloneSettings
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots import app as main_bot, logger, config
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
async def get_stats(admin: str = Depends(get_current_admin)):
    total_users = await database.db.users.count_documents({})
    total_chats = await database.db.chats.count_documents({})
    active_clones = await database.db.clones.count_documents({"status": "active"})
    premium_users = await database.db.users.count_documents({"is_premium": True})

    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "active_players": len(clone_manager.clones),
        "premium_users": premium_users,
        "cloned_bots": active_clones,
        "revenue_tracking": premium_users * 10
    }

@app.post("/api/premium/grant")
async def grant_premium(user_id: int = Body(...), days: int = Body(0), admin: str = Depends(get_current_admin)):
    expiry = (datetime.now(timezone.utc) + timedelta(days=days)) if days > 0 else None
    await database.update_user(user_id, is_premium=True, premium_expiry=expiry)
    return {"status": "success"}

@app.get("/api/settings")
async def get_global_settings(admin: str = Depends(get_current_admin)):
    settings = await database.get_settings()
    return settings.to_dict() if settings else {}

@app.post("/api/settings/toggle")
async def toggle_global_setting(flag: str = Body(...), value: bool = Body(...), admin: str = Depends(get_current_admin)):
    await database.update_settings(None, **{flag: value})
    return {"status": "success", "flag": flag, "new_value": value}

@app.post("/api/broadcast")
async def global_broadcast(
    message: str = Body(...),
    target: str = Body("all"),
    admin: str = Depends(get_current_admin)
):
    user_ids = await database.get_all_users()

    async def run_broadcast():
        if target in ["all", "main"]:
            for uid in user_ids:
                try: await main_bot.send_message(uid, message); await asyncio.sleep(0.05)
                except: pass

        if target in ["all", "clones"]:
            for client in clone_manager.clones.values():
                try: await client.send_message(config.OWNER_ID, f"NARZOXBOTS BROADCAST:\n\n{message}")
                except: pass

    asyncio.create_task(run_broadcast())
    return {"status": "success"}

@app.get("/", response_class=HTMLResponse)
async def read_item():
    with open("web/templates/index.html") as f:
        return f.read()

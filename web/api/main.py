from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from NarzoxBots.database.db import get_db, json_db
from NarzoxBots.database.models import User, Chat, Clone, AdminAction, Broadcast, GlobalSettings, CloneSettings
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
    total_users = len(json_db.data["users"])
    total_chats = len(json_db.data["chats"])
    active_clones = len([c for c in json_db.data["clones"].values() if c.get("status") == "active"])
    premium_users = len([u for u in json_db.data["users"].values() if u.get("is_premium")])

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
    expiry = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat() if days > 0 else None
    if str(user_id) in json_db.data["users"]:
        json_db.data["users"][str(user_id)].update({"is_premium": True, "premium_expiry": expiry})
        await json_db._save()
    return {"status": "success"}

@app.get("/api/settings")
async def get_global_settings(admin: str = Depends(get_current_admin)):
    return json_db.data["global_settings"].get("1", {})

@app.post("/api/settings/toggle")
async def toggle_global_setting(flag: str = Body(...), value: bool = Body(...), admin: str = Depends(get_current_admin)):
    if "1" in json_db.data["global_settings"]:
        json_db.data["global_settings"]["1"][flag] = value
        await json_db._save()
        return {"status": "success", "flag": flag, "new_value": value}
    raise HTTPException(status_code=404, detail="Settings not found")

@app.post("/api/broadcast")
async def global_broadcast(
    message: str = Body(...),
    target: str = Body("all"),
    admin: str = Depends(get_current_admin)
):
    user_ids = [int(uid) for uid in json_db.data["users"].keys()]

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

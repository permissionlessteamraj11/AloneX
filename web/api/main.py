from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from NarzoxBots.database.db import get_db, async_session
from NarzoxBots.database.models import User, Clone, AdminAction, Broadcast
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots import app as main_bot, logger
from sqlalchemy import select, func
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
from config import Config

config = Config()
SECRET_KEY = config.ENCRYPTION_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Supreme Panel API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real system, you would check against a secure admin table
    # Here we check against the OWNER_ID from config for simplicity
    if form_data.username == str(config.OWNER_ID): # Use owner ID as username
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.get("/stats")
async def get_stats(admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    total_users = await db.execute(select(func.count(User.id)))
    active_clones = await db.execute(select(func.count(Clone.id)).where(Clone.status == "active"))
    premium_users = await db.execute(select(func.count(User.id)).where(User.is_premium == True))

    return {
        "total_users": total_users.scalar(),
        "active_clones": active_clones.scalar(),
        "premium_users": premium_users.scalar()
    }

@app.get("/api/clones")
async def list_clones(admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Clone))
    clones = result.scalars().all()

    statuses = await clone_manager.get_all_clones_status()

    output = []
    for c in clones:
        output.append({
            "id": c.id,
            "owner_id": c.owner_id,
            "bot_username": c.bot_username,
            "bot_name": c.bot_name,
            "status": c.status,
            "is_connected": statuses.get(c.bot_token, {}).get("is_connected", False)
        })
    return output

@app.post("/api/clones/{clone_id}/restart")
async def restart_clone_api(clone_id: int, admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Clone).where(Clone.id == clone_id))
    clone = result.scalar_one_or_none()
    if not clone:
        raise HTTPException(status_code=404, detail="Clone not found")

    await clone_manager.restart_clone(clone.bot_token)
    return {"status": "success", "message": f"Clone {clone.bot_username} restarted"}

@app.get("/", response_class=HTMLResponse)
async def read_item():
    with open("web/templates/index.html") as f:
        return f.read()

@app.get("/api/users")
async def list_users(page: int = 1, limit: int = 20, admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    result = await db.execute(select(User).offset(offset).limit(limit))
    users = result.scalars().all()
    return users

@app.post("/api/broadcast")
async def global_broadcast(message: str, admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    # Get all users
    result = await db.execute(select(User))
    users = result.scalars().all()
    user_ids = [u.id for u in users]

    # Create broadcast record
    new_broadcast = Broadcast(
        sender_id=int(admin),
        message_data={"text": message},
        status="processing",
        total_users=len(user_ids)
    )
    db.add(new_broadcast)
    await db.commit()
    await db.refresh(new_broadcast)

    # Start background broadcast task
    async def run_broadcast():
        sent = 0
        for user_id in user_ids:
            try:
                await main_bot.send_message(user_id, message)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"Broadcast failed for {user_id}: {e}")

        async with async_session() as session:
            result = await session.execute(select(Broadcast).where(Broadcast.id == new_broadcast.id))
            b = result.scalar_one_or_none()
            if b:
                b.sent_count = sent
                b.status = "completed"
            await session.commit()

    asyncio.create_task(run_broadcast())

    return {"status": "success", "total_users": len(user_ids), "message": "Broadcast initiated in background"}

@app.post("/admin/grant-premium/{user_id}")
async def grant_premium(user_id: int, days: int, admin: str = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(id=user_id, is_premium=True)
        db.add(user)
    else:
        user.is_premium = True

    # Audit log
    action = AdminAction(
        admin_id=int(admin),
        action="GRANT_PREMIUM",
        target_id=user_id,
        reason=f"Granted {days} days"
    )
    db.add(action)

    await db.commit()
    return {"status": "success", "message": f"Premium granted to {user_id}"}

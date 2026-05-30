from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from NarzoxBots.database.db import get_db
from NarzoxBots.database.models import User, Clone, AdminAction, Broadcast
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

@app.get("/", response_class=HTMLResponse)
async def read_item():
    with open("web/templates/index.html") as f:
        return f.read()

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

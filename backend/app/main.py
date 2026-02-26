from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import SessionLocal, get_db
from app.core.security import create_access_token
from app.models.user import User
import os

app = FastAPI(title="Ava AI Backend v1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Ava AI Backend v1.1 rodando!", "version": "1.1.0"}


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}


@app.post("/auth/register")
async def register(
    name: str,
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    # Hash senha
    from app.core.security import hash_password
    password_hash = hash_password(password)

    # Cria user
    result = await db.execute(
        text("""
        INSERT INTO users (name, email, password_hash) 
        VALUES (:name, :email, :password_hash)
        RETURNING id
        """),
        {"name": name, "email": email, "password_hash": password_hash}
    )
    user_id = result.scalar()
    await db.commit()
    return {"user_id": str(user_id), "email": email}


@app.post("/auth/login")
async def login(
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    from app.core.security import verify_password, create_access_token

    # Busca user
    result = await db.execute(
        text("SELECT * FROM users WHERE email = :email AND is_active = true"),
        {"email": email}
    )
    user = result.fetchone()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

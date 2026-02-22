import os
import jwt
import datetime
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from passlib.hash import bcrypt

app = FastAPI()

# Configuration
DB_PATH = "sqlite.db"
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key")
ALGORITHM = "HS256"

# Models
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Database helper
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    # Add a default user for testing if not exists
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       ("admin", bcrypt.hash("admin123")))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

# Authentication Logic
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    to_encode.update({
        "exp": expire,
        "iss": "kong-issuer"  # Match the key in Kong JWT credential
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Endpoints
@app.post("/login", response_model=Token)
def login(user: User):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user or not bcrypt.verify(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/verify")
def verify(authorization: Optional[str] = Header(None)):
    if not authorization or not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    parts = authorization.split(" ")
    if len(parts) < 2:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"status": "valid", "user": payload.get("sub")}

@app.get("/users")
def get_users(authorization: Optional[str] = Header(None)):
    if not authorization or not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authorized")
    
    parts = authorization.split(" ")
    if len(parts) < 2:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = parts[1]
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return [{"id": u["id"], "username": u["username"]} for u in users]

@app.get("/health")
def health():
    return {"status": "healthy"}

import hashlib
import hmac
import secrets
import sqlite3
import uuid
from pathlib import Path
import database

ROOT = Path(__file__).resolve().parent
AUTH_DB = ROOT / "users.db"
ITERATIONS = 310_000

def initialize_auth_db():
    with sqlite3.connect(AUTH_DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_salt BLOB NOT NULL,
            password_hash BLOB NOT NULL,
            db_filename TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)

def register(email, password):
    email = email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Enter a valid email address.")
    if len(password) < 10:
        raise ValueError("Use a password with at least 10 characters.")
    salt = secrets.token_bytes(16)
    digest = _hash_password(password, salt)
    user_id = str(uuid.uuid4())
    db_filename = f"{user_id}.db"
    try:
        with sqlite3.connect(AUTH_DB) as conn:
            conn.execute("""INSERT INTO users
                (id,email,password_salt,password_hash,db_filename)
                VALUES (?,?,?,?,?)""",
                (user_id, email, salt, digest, db_filename))
    except sqlite3.IntegrityError:
        raise ValueError("An account with that email already exists.")
    database.initialize_user_database(db_filename)
    return {"id": user_id, "email": email, "db_filename": db_filename}

def login(email, password):
    with sqlite3.connect(AUTH_DB) as conn:
        row = conn.execute("""SELECT id,email,password_salt,password_hash,db_filename
            FROM users WHERE email=? COLLATE NOCASE""", (email.strip(),)).fetchone()
    if not row:
        return None
    user_id, saved_email, salt, expected, db_filename = row
    actual = _hash_password(password, salt)
    if not hmac.compare_digest(actual, expected):
        return None
    return {"id": user_id, "email": saved_email, "db_filename": db_filename}

import sqlite3
import hashlib
import secrets
import hmac
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "spam_detection.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_auth_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310000
    ).hex()

    return password_hash, salt


def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    password_hash, salt = hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, salt))

        conn.commit()
        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

    finally:
        conn.close()


def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, email, password_hash, salt
        FROM users
        WHERE username = ?
    """, (username.strip(),))

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return False, None

    user_id, saved_username, email, saved_hash, salt = user

    entered_hash, _ = hash_password(password, salt)

    if hmac.compare_digest(entered_hash, saved_hash):
        return True, {
            "id": user_id,
            "username": saved_username,
            "email": email
        }

    return False, None
import os
import secrets
import sqlite3

from werkzeug.security import generate_password_hash


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "student_performance.db")


def get_connection():
    """Create and return a database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the prediction history + users tables if they do not exist."""

    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_data TEXT NOT NULL,
                predicted_grade REAL NOT NULL,
                performance_level TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student',
                token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        print("Database initialized successfully!")

    finally:
        connection.close()


def create_user(name, email, password, role):
    """Create a new user with a hashed password and a session token."""
    password_hash = generate_password_hash(password)
    token = secrets.token_hex(32)

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (name, email, password_hash, role, token)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, password_hash, role, token),
        )
        connection.commit()
        user_id = cursor.lastrowid
    finally:
        connection.close()

    return {
        "id": user_id,
        "name": name,
        "email": email,
        "role": role,
        "token": token,
    }


def get_user_by_email(email):
    """Return the user row for an email, or None."""
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def get_user_by_token(token):
    """Return the user row for a session token, or None."""
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT * FROM users WHERE token = ?",
            (token,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def delete_token(token):
    """Invalidate a session token (logout)."""
    connection = get_connection()

    try:
        connection.execute(
            "UPDATE users SET token = NULL WHERE token = ?",
            (token,),
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()

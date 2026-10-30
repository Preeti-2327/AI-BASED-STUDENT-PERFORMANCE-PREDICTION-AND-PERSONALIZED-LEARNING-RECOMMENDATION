"""Database layer for the AI-Based Student Performance Prediction system.

Supports TWO backends, selected with the ``DB_ENGINE`` environment variable:

- ``sqlite`` (DEFAULT) → file-based database at
  ``<project root>/student_performance.db`` (overridable via ``SQLITE_PATH``).
  Used for local development / demo runs. Creates all tables + seeds demo data.
- ``mysql`` → MySQL server (``MYSQL_HOST``, ``MYSQL_PORT``, ``MYSQL_USER``,
  ``MYSQL_PASSWORD``, ``MYSQL_DB`` env vars), as before.

Every public function below keeps a stable Python-level API so
``backend/app.py`` does not need to change:
  - get_connection(include_db=False)
  - initialize_database()
  - create_user / get_user_by_email / get_user_by_token / delete_token
  - save_prediction / get_all_predictions / delete_prediction
"""

import os
import json
import secrets
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLITE_PATH = os.environ.get("SQLITE_PATH") or os.path.join(BASE_DIR, "student_performance.db")
DB_ENGINE = (os.environ.get("DB_ENGINE") or "sqlite").strip().lower() or "sqlite"

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "Anjali@123"),
    "database": os.environ.get("MYSQL_DB", "student_performance_db"),
    "charset": "utf8mb4",
    "cursorclass": None,  # pymysql.cursors.DictCursor set below via connect() args
    "autocommit": True,
}


# ------------------------------------------------------------
# CONNECTION
# ------------------------------------------------------------
def get_connection(include_db=True):
    """Create and return a database connection (sqlite by default)."""
    if DB_ENGINE == "mysql":
        import pymysql
        import pymysql.cursors

        cfg = dict(MYSQL_CONFIG)
        if not include_db:
            cfg.pop("database", None)
        cfg["cursorclass"] = pymysql.cursors.DictCursor
        return pymysql.connect(**cfg)

    # SQLite (default)
    conn = sqlite3.connect(SQLITE_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ------------------------------------------------------------
# SCHEMA
# ------------------------------------------------------------
def _create_mysql_schema(cursor):
    cursor.execute("""
        CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """ % MYSQL_CONFIG["database"])
    cursor.execute("USE `%s`;" % MYSQL_CONFIG["database"])

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student',
            token VARCHAR(128) UNIQUE NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_email (email),
            INDEX idx_user_role (role)
        ) ENGINE=InnoDB;
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_code VARCHAR(20) NOT NULL UNIQUE,
            user_id INT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            subject VARCHAR(100) NOT NULL,
            classes_count INT NOT NULL DEFAULT 1,
            status ENUM('Active', 'On Leave', 'Inactive') DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB;
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            teacher_name VARCHAR(100) NOT NULL,
            teacher_id INT NULL,
            credits INT NOT NULL DEFAULT 3,
            students_count INT NOT NULL DEFAULT 0,
            color VARCHAR(20) DEFAULT '#2c7be5',
            progress INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
        ) ENGINE=InnoDB;
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_code VARCHAR(20) NOT NULL UNIQUE,
            user_id INT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            grade_class VARCHAR(20) NOT NULL DEFAULT '10-A',
            level ENUM('Needs Improvement', 'Average', 'Good', 'Excellent') NOT NULL DEFAULT 'Average',
            attendance_pct INT NOT NULL DEFAULT 85,
            avg_grade DECIMAL(4, 1) NOT NULL DEFAULT 12.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_student_level (level)
        ) ENGINE=InnoDB;
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NULL,
            student_email VARCHAR(120) NULL,
            predicted_grade DECIMAL(4, 1) NOT NULL,
            performance_level VARCHAR(50) NOT NULL,
            recommendations JSON NOT NULL,
            student_data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL,
            INDEX idx_pred_created (created_at),
            INDEX idx_pred_level (performance_level)
        ) ENGINE=InnoDB;
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_study_habits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_email VARCHAR(120) NOT NULL UNIQUE,
            hours_per_day DECIMAL(3, 1) DEFAULT 2.0,
            focus_subject VARCHAR(100) DEFAULT 'Mathematics',
            revision_days INT DEFAULT 3,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            record_date DATE NOT NULL,
            student_code VARCHAR(20) NOT NULL,
            is_present BOOLEAN NOT NULL DEFAULT TRUE,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_date_student (record_date, student_code)
        ) ENGINE=InnoDB;
    """)


def _create_sqlite_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON users (email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_role ON users (role);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_code TEXT NOT NULL UNIQUE,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            subject TEXT NOT NULL,
            classes_count INTEGER NOT NULL DEFAULT 1,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            teacher_name TEXT NOT NULL,
            teacher_id INTEGER,
            credits INTEGER NOT NULL DEFAULT 3,
            students_count INTEGER NOT NULL DEFAULT 0,
            color TEXT DEFAULT '#2c7be5',
            progress INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id) ON DELETE SET NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_code TEXT NOT NULL UNIQUE,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            grade_class TEXT NOT NULL DEFAULT '10-A',
            level TEXT NOT NULL DEFAULT 'Average',
            attendance_pct INTEGER NOT NULL DEFAULT 85,
            avg_grade REAL NOT NULL DEFAULT 12.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_student_level ON students (level);
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            student_email TEXT,
            predicted_grade REAL NOT NULL,
            performance_level TEXT NOT NULL,
            recommendations TEXT NOT NULL,
            student_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_study_habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT NOT NULL UNIQUE,
            hours_per_day REAL DEFAULT 2.0,
            focus_subject TEXT DEFAULT 'Mathematics',
            revision_days INTEGER DEFAULT 3,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,
            student_code TEXT NOT NULL,
            is_present INTEGER NOT NULL DEFAULT 1,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (record_date, student_code)
        )
    """)


def initialize_database():
    """Create the database, all relational tables, and seed initial demo data."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            root_conn = get_connection(include_db=False)
            try:
                with root_conn.cursor() as root_cursor:
                    root_cursor.execute(
                        "CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                        % MYSQL_CONFIG["database"]
                    )
            finally:
                root_conn.close()
            conn.close()
            conn = get_connection(include_db=True)
            cursor = conn.cursor()

        if DB_ENGINE == "mysql":
            _create_mysql_schema(cursor)
        else:
            _create_sqlite_schema(cursor)

        cursor.execute("SELECT COUNT(*) AS cnt FROM users;")
        if cursor.fetchone()["cnt"] == 0:
            seed_default_data(cursor)

        print(f"[DB] Database initialized successfully! (engine={DB_ENGINE})")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def seed_default_data(cursor):
    """Seed initial demo accounts, teachers, subjects, and students."""
    users = [
        ("Demo Admin", "admin@school.edu", "admin123", "admin"),
        ("Meera Nair", "meera@school.edu", "teacher123", "teacher"),
        ("Rahul Verma", "rahul@school.edu", "teacher123", "teacher"),
        ("Sara Khan", "sara@school.edu", "teacher123", "teacher"),
        ("Demo Student", "student@example.com", "student123", "student"),
        ("Aarav Sharma", "aarav@example.com", "student123", "student"),
        ("Diya Patel", "diya@example.com", "student123", "student"),
        ("Kabir Singh", "kabir@example.com", "student123", "student"),
        ("Ananya Iyer", "ananya@example.com", "student123", "student"),
        ("Vivaan Rao", "vivaan@example.com", "student123", "student"),
    ]

    for name, email, pwd, role in users:
        token = secrets.token_hex(32)
        pwd_hash = generate_password_hash(pwd)
        if DB_ENGINE == "mysql":
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, token) VALUES (%s, %s, %s, %s, %s);",
                (name, email, pwd_hash, role, token),
            )
        else:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, token) VALUES (?, ?, ?, ?, ?);",
                (name, email, pwd_hash, role, token),
            )

    teachers = [
        ("TCH-01", "Meera Nair", "meera@school.edu", "Mathematics", 4, "Active"),
        ("TCH-02", "Rahul Verma", "rahul@school.edu", "Science", 3, "Active"),
        ("TCH-03", "Sara Khan", "sara@school.edu", "English", 5, "On Leave"),
    ]
    for code, name, email, subject, classes, status in teachers:
        if DB_ENGINE == "mysql":
            cursor.execute(
                "INSERT INTO teachers (teacher_code, name, email, subject, classes_count, status) VALUES (%s, %s, %s, %s, %s, %s);",
                (code, name, email, subject, classes, status),
            )
        else:
            cursor.execute(
                "INSERT INTO teachers (teacher_code, name, email, subject, classes_count, status) VALUES (?, ?, ?, ?, ?, ?);",
                (code, name, email, subject, classes, status),
            )

    subjects = [
        ("MATH-10", "Mathematics", "Meera Nair", 4, 58, "#2c7be5", 72),
        ("SCI-10", "Science", "Rahul Verma", 4, 55, "#28a745", 64),
        ("ENG-10", "English", "Sara Khan", 3, 60, "#f0ad4e", 81),
        ("SST-09", "Social Science", "Rahul Verma", 3, 47, "#6f42c1", 58),
    ]
    for code, name, teacher, credits, students, color, progress in subjects:
        if DB_ENGINE == "mysql":
            cursor.execute(
                "INSERT INTO subjects (code, name, teacher_name, teacher_id, credits, students_count, color, progress) VALUES (%s, %s, %s, NULL, %s, %s, %s, %s);",
                (code, name, teacher, credits, students, color, progress),
            )
        else:
            cursor.execute(
                "INSERT INTO subjects (code, name, teacher_name, teacher_id, credits, students_count, color, progress) VALUES (?, ?, ?, NULL, ?, ?, ?, ?);",
                (code, name, teacher, credits, students, color, progress),
            )

    students = [
        ("STU-001", "Aarav Sharma", "aarav@example.com", "10-A", "Good", 92, 14.2),
        ("STU-002", "Diya Patel", "diya@example.com", "10-B", "Excellent", 97, 17.1),
        ("STU-003", "Kabir Singh", "kabir@example.com", "9-A", "Needs Improvement", 68, 8.4),
        ("STU-004", "Ananya Iyer", "ananya@example.com", "10-A", "Average", 84, 11.6),
        ("STU-005", "Vivaan Rao", "vivaan@example.com", "9-B", "Good", 90, 13.8),
    ]
    for code, name, email, grade_class, level, att, avg in students:
        if DB_ENGINE == "mysql":
            cursor.execute(
                "INSERT INTO students (student_code, name, email, grade_class, level, attendance_pct, avg_grade) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (code, name, email, grade_class, level, att, avg),
            )
        else:
            cursor.execute(
                "INSERT INTO students (student_code, name, email, grade_class, level, attendance_pct, avg_grade) VALUES (?, ?, ?, ?, ?, ?, ?);",
                (code, name, email, grade_class, level, att, avg),
            )


# ------------------------------------------------------------
# USER CRUD FUNCTIONS
# ------------------------------------------------------------
def create_user(name, email, password, role="student"):
    """Create a new user with hashed password and session token."""
    password_hash = generate_password_hash(password)
    token = secrets.token_hex(32)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, token) VALUES (%s, %s, %s, %s, %s);",
                (name, email, password_hash, role, token),
            )
        else:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, token) VALUES (?, ?, ?, ?, ?);",
                (name, email, password_hash, role, token),
            )
        if role == "student":
            student_code = f"STU-{secrets.randbelow(900) + 100}"
            if DB_ENGINE == "mysql":
                cursor.execute(
                    "INSERT IGNORE INTO students (student_code, name, email, grade_class, level, attendance_pct, avg_grade) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (student_code, name, email, "10-A", "Average", 85, 12.0),
                )
            else:
                cursor.execute(
                    "INSERT OR IGNORE INTO students (student_code, name, email, grade_class, level, attendance_pct, avg_grade) VALUES (?, ?, ?, ?, ?, ?, ?);",
                    (student_code, name, email, "10-A", "Average", 85, 12.0),
                )
        return {"token": token, "role": role, "name": name, "email": email}
    finally:
        conn.close()


def get_user_by_email(email):
    """Retrieve user record by email."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
        else:
            cursor.execute("SELECT * FROM users WHERE email = ?;", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_token(token):
    """Retrieve user record by session token."""
    if not token:
        return None
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            cursor.execute("SELECT * FROM users WHERE token = %s;", (token,))
        else:
            cursor.execute("SELECT * FROM users WHERE token = ?;", (token,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_token(token):
    """Log out a user by invalidating session token."""
    if not token:
        return
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            cursor.execute("UPDATE users SET token = NULL WHERE token = %s;", (token,))
        else:
            cursor.execute("UPDATE users SET token = NULL WHERE token = ?;", (token,))
    finally:
        conn.close()


# ------------------------------------------------------------
# PREDICTION HISTORY FUNCTIONS
# ------------------------------------------------------------
def save_prediction(student_data, predicted_grade, performance_level, recommendations):
    """Save an AI prediction record to the predictions table."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        email = student_data.get("email") if isinstance(student_data, dict) else None
        student_id = None
        if email:
            if DB_ENGINE == "mysql":
                cursor.execute("SELECT id FROM students WHERE email = %s;", (email,))
            else:
                cursor.execute("SELECT id FROM students WHERE email = ?;", (email,))
            s_row = cursor.fetchone()
            if s_row:
                student_id = s_row["id"]

        if DB_ENGINE == "mysql":
            cursor.execute("""
                INSERT INTO predictions (student_id, student_email, predicted_grade, performance_level, recommendations, student_data)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                student_id,
                email,
                float(predicted_grade),
                str(performance_level),
                json.dumps(recommendations),
                json.dumps(student_data),
            ))
        else:
            cursor.execute("""
                INSERT INTO predictions (student_id, student_email, predicted_grade, performance_level, recommendations, student_data)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                student_id,
                email,
                float(predicted_grade),
                str(performance_level),
                json.dumps(recommendations),
                json.dumps(student_data),
            ))
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_predictions(limit=50):
    """Fetch recent predictions."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT %s;", (limit,))
        else:
            cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT ?;", (limit,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            row = dict(r)
            if isinstance(row.get("recommendations"), (str, bytes, bytearray)):
                row["recommendations"] = json.loads(row["recommendations"])
            if isinstance(row.get("student_data"), (str, bytes, bytearray)):
                row["student_data"] = json.loads(row["student_data"])
            if row.get("created_at"):
                try:
                    row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    row["created_at"] = str(row["created_at"])
            results.append(row)
        return results
    finally:
        conn.close()


def delete_prediction(prediction_id):
    """Delete a prediction by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            cursor.execute("DELETE FROM predictions WHERE id = %s;", (prediction_id,))
        else:
            cursor.execute("DELETE FROM predictions WHERE id = ?;", (prediction_id,))
        return cursor.rowcount > 0
    finally:
        conn.close()

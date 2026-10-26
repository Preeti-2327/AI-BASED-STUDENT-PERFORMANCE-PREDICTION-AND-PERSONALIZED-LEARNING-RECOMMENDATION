import os
import json
import secrets
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------------------------------------------------
# MYSQL DATABASE CONFIGURATION
# ------------------------------------------------------------
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "Anjali@123"),
    "database": os.environ.get("MYSQL_DB", "student_performance_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True
}


def get_connection(include_db=True):
    """Create and return a MySQL connection."""
    cfg = MYSQL_CONFIG.copy()
    if not include_db:
        cfg.pop("database", None)
    return pymysql.connect(**cfg)


def initialize_database():
    """Create the database, all relational tables, and seed initial demo data."""
    # 1. Create database if it does not exist
    root_conn = get_connection(include_db=False)
    try:
        with root_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    finally:
        root_conn.close()

    # 2. Execute table creations
    conn = get_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            # Users
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

            # Teachers
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

            # Subjects
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

            # Students
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

            # Predictions
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

            # Habits
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

            # Attendance records
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

            # Seed default users if empty
            cursor.execute("SELECT COUNT(*) AS cnt FROM users;")
            if cursor.fetchone()["cnt"] == 0:
                seed_default_data(cursor)

        print("[MySQL] Database initialized successfully!")
    finally:
        conn.close()


def seed_default_data(cursor):
    """Seed initial demo accounts, teachers, subjects, and students."""
    # 1. Demo users
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
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, token) VALUES (%s, %s, %s, %s, %s);",
            (name, email, pwd_hash, role, token)
        )

    # 2. Teachers
    teachers = [
        ("TCH-01", "Meera Nair", "meera@school.edu", "Mathematics", 4, "Active"),
        ("TCH-02", "Rahul Verma", "rahul@school.edu", "Science", 3, "Active"),
        ("TCH-03", "Sara Khan", "sara@school.edu", "English", 5, "On Leave"),
    ]
    for code, name, email, subject, classes, status in teachers:
        cursor.execute(
            "INSERT INTO teachers (teacher_code, name, email, subject, classes_count, status) VALUES (%s, %s, %s, %s, %s, %s);",
            (code, name, email, subject, classes, status)
        )

    # 3. Subjects
    subjects = [
        ("MATH-10", "Mathematics", "Meera Nair", 4, 58, "#2c7be5", 72),
        ("SCI-10", "Science", "Rahul Verma", 4, 55, "#28a745", 64),
        ("ENG-10", "English", "Sara Khan", 3, 60, "#f0ad4e", 81),
        ("SST-09", "Social Science", "Rahul Verma", 3, 47, "#6f42c1", 58),
    ]
    for code, name, teacher, credits, students, color, progress in subjects:
        cursor.execute(
            "INSERT INTO subjects (code, name, teacher_name, credits, students_count, color, progress) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (code, name, teacher, credits, students, color, progress)
        )

    # 4. Students
    students = [
        ("STU-001", "Aarav Sharma", "aarav@example.com", "10-A", "Good", 92, 14.2),
        ("STU-002", "Diya Patel", "diya@example.com", "10-B", "Excellent", 97, 17.1),
        ("STU-003", "Kabir Singh", "kabir@example.com", "9-A", "Needs Improvement", 68, 8.4),
        ("STU-004", "Ananya Iyer", "ananya@example.com", "10-A", "Average", 84, 11.6),
        ("STU-005", "Vivaan Rao", "vivaan@example.com", "9-B", "Good", 90, 13.8),
    ]
    for code, name, email, grade_class, level, att, avg in students:
        cursor.execute(
            "INSERT INTO students (student_code, name, email, grade_class, level, attendance_pct, avg_grade) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (code, name, email, grade_class, level, att, avg)
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
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, token) VALUES (%s, %s, %s, %s, %s);",
                (name, email, password_hash, role, token)
            )
            # If student, also add to students table
            if role == "student":
                student_code = f"STU-{secrets.randbelow(900) + 100}"
                cursor.execute(
                    "INSERT IGNORE INTO students (student_code, name, email, grade_class, level, attendance_pct, avg_grade) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (student_code, name, email, "10-A", "Average", 85, 12.0)
                )
        return {"token": token, "role": role, "name": name, "email": email}
    finally:
        conn.close()


def get_user_by_email(email):
    """Retrieve user record by email."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_user_by_token(token):
    """Retrieve user record by session token."""
    if not token:
        return None
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE token = %s;", (token,))
            return cursor.fetchone()
    finally:
        conn.close()


def delete_token(token):
    """Log out a user by invalidating session token."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET token = NULL WHERE token = %s;", (token,))
    finally:
        conn.close()


# ------------------------------------------------------------
# PREDICTION HISTORY FUNCTIONS
# ------------------------------------------------------------
def save_prediction(student_data, predicted_grade, performance_level, recommendations):
    """Save an AI prediction record to MySQL."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            email = student_data.get("email") if isinstance(student_data, dict) else None
            student_id = None
            if email:
                cursor.execute("SELECT id FROM students WHERE email = %s;", (email,))
                s_row = cursor.fetchone()
                if s_row:
                    student_id = s_row["id"]

            cursor.execute("""
                INSERT INTO predictions (student_id, student_email, predicted_grade, performance_level, recommendations, student_data)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                student_id,
                email,
                float(predicted_grade),
                str(performance_level),
                json.dumps(recommendations),
                json.dumps(student_data)
            ))
            return cursor.lastrowid
    finally:
        conn.close()


def get_all_predictions(limit=50):
    """Fetch recent predictions from MySQL."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT %s;", (limit,))
            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r.get("recommendations"), str):
                    r["recommendations"] = json.loads(r["recommendations"])
                if isinstance(r.get("student_data"), str):
                    r["student_data"] = json.loads(r["student_data"])
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            return rows
    finally:
        conn.close()


def delete_prediction(prediction_id):
    """Delete a prediction by ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM predictions WHERE id = %s;", (prediction_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()

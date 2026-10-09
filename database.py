
import sqlite3


DATABASE_NAME = "student_performance.db"


def get_connection():
    """Create and return a database connection."""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the prediction history table if it does not exist."""

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

        connection.commit()
        print("Database initialized successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
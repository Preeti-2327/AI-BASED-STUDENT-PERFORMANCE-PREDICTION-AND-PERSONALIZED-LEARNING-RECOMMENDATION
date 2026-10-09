
from database import get_connection

connection = get_connection()

try:
    rows = connection.execute(
        """
        SELECT id, predicted_grade, performance_level, created_at
        FROM predictions
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    if rows:
        print("Saved predictions:")
        for row in rows:
            print(dict(row))
    else:
        print("No predictions have been saved yet.")

finally:
    connection.close()
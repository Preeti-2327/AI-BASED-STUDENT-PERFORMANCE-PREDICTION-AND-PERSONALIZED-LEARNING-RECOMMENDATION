"""Quick sanity check for the predictions table.

Run from the project root (or backend/):

    python backend/check_database.py
"""

from database import get_all_predictions


def main():
    history = get_all_predictions(limit=5)

    if history:
        print("Saved predictions:")
        for row in history:
            print(row)
    else:
        print("No predictions have been saved yet.")

    return history


if __name__ == "__main__":
    main()

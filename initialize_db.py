import sqlite3


def initialize_db(db_path="moviweb_app.db"):
    """Initialize the SQLite database and create the necessary tables."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,  -- Changed from 'name' to 'title'
            director TEXT NOT NULL,
            year INTEGER,
            rating REAL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """)

        print("Database works successfully!")


if __name__ == "__main__":
    initialize_db()

import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/magentrace.db")


def get_connection():
    """
    Create and return a connection to the local SQLite database.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    """
    Create the first database tables for the MagenTrace AI prototype.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            robot_name TEXT,
            software_stack TEXT,
            description TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT,
            severity TEXT,
            source TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS joint_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            joint_name TEXT NOT NULL,
            position REAL,
            velocity REAL,
            effort REAL,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
import sqlite3

conn = sqlite3.connect(
    "sessions/langgraph.db",
    check_same_thread=False
)
def create_threads_table(conn):

    conn.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
create_threads_table(conn)
def get_db_connection():
    return conn
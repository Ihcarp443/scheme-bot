from db.sqlite import get_db_connection


def create_threads_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()


def save_thread(
    thread_id: str,
    title: str
):
    
    conn = get_db_connection()

    conn.execute(
        """
        INSERT OR REPLACE INTO threads (
            thread_id,
            title
        )
        VALUES (?, ?)
        """,
        (
            thread_id,
            title
        )
    )

    conn.commit()
    conn.close()


def get_all_threads():
    conn = get_db_connection()

    cursor = conn.execute(
        """
        SELECT
            thread_id,
            title,
            created_at
        FROM threads
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "thread_id": row[0],
            "title": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]

    

def get_thread(
    thread_id: str
):
    conn = get_db_connection()

    cursor = conn.execute(
        """
        SELECT
            thread_id,
            title,
            created_at
        FROM threads
        WHERE thread_id = ?
        """,
        (thread_id,)
    )

    row = cursor.fetchone()

    conn.close()
    if not row:
        return None
    
    return {
        "thread_id": row[0],
        "title": row[1],
        "created_at": row[2]
    }


def delete_thread(
    thread_id: str
):
    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM threads
        WHERE thread_id = ?
        """,
        (thread_id,)
    )

    conn.commit()
    conn.close()
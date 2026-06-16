# db/feedback_repository.py

from db.sqlite import get_db_connection

def save_feedback(
    thread_id: str,
    answer: str,
    feedback: str
):
    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO feedback
        (
            thread_id,
            answer,
            feedback
        )
        VALUES (?, ?, ?)
        """,
        (
            thread_id,
            answer,
            feedback
        )
    )

    conn.commit()
    conn.close()
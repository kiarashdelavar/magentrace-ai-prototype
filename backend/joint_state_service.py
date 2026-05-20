from datetime import datetime, timezone

from backend.database import create_tables, get_connection
from backend.event_service import check_session_exists


def get_current_time():
    return datetime.now(timezone.utc).isoformat()


def add_joint_state(session_id, joint_name, position, velocity=None, effort=None):
    create_tables()
    check_session_exists(session_id)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO joint_states (
            session_id,
            timestamp,
            joint_name,
            position,
            velocity,
            effort
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            get_current_time(),
            joint_name,
            position,
            velocity,
            effort,
        ),
    )

    joint_state_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return joint_state_id


def get_joint_states_for_session(session_id):
    create_tables()
    check_session_exists(session_id)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, session_id, timestamp, joint_name, position, velocity, effort
        FROM joint_states
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """,
        (session_id,),
    )

    rows = cursor.fetchall()
    connection.close()

    return rows
from datetime import datetime, timezone
from backend.database import get_connection, create_tables


def get_current_time():
    """
    Return the current UTC time as an ISO formatted string.
    """
    return datetime.now(timezone.utc).isoformat()


def start_session(name, robot_name=None, software_stack=None, description=None):
    """
    Start a new robot test session and save it in the database.

    Args:
        name: Name of the test session.
        robot_name: Name of the robot used in the session.
        software_stack: Software stack used during the test.
        description: Short description of the session.

    Returns:
        The ID of the created session.
    """
    if not name or not name.strip():
        raise ValueError("Session name is required.")

    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO sessions (
            name,
            robot_name,
            software_stack,
            description,
            start_time,
            end_time,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name.strip(),
            robot_name,
            software_stack,
            description,
            get_current_time(),
            None,
            "active",
        ),
    )

    session_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return session_id


def stop_session(session_id):
    """
    Stop an active robot test session.

    Args:
        session_id: ID of the session that should be stopped.

    Returns:
        True if the session was stopped.
    """
    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, status
        FROM sessions
        WHERE id = ?
        """,
        (session_id,),
    )

    session = cursor.fetchone()

    if session is None:
        connection.close()
        raise ValueError(f"No session found with ID {session_id}.")

    if session[1] == "stopped":
        connection.close()
        raise ValueError(f"Session {session_id} is already stopped.")

    cursor.execute(
        """
        UPDATE sessions
        SET end_time = ?, status = ?
        WHERE id = ?
        """,
        (get_current_time(), "stopped", session_id),
    )

    connection.commit()
    connection.close()

    return True


def get_all_sessions():
    """
    Get all sessions from the database.

    Returns:
        A list of session rows.
    """
    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, robot_name, software_stack, description, start_time, end_time, status
        FROM sessions
        ORDER BY id DESC
        """
    )

    sessions = cursor.fetchall()
    connection.close()

    return sessions


def get_active_session():
    """
    Get the latest active session.

    Returns:
        The active session row, or None if there is no active session.
    """
    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, robot_name, software_stack, description, start_time, end_time, status
        FROM sessions
        WHERE status = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        ("active",),
    )

    session = cursor.fetchone()
    connection.close()

    return session
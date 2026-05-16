from datetime import datetime, timezone

from backend.database import get_connection, create_tables


VALID_EVENT_TYPES = {
    "overshoot",
    "sudden_acceleration",
    "unexpected_stop",
    "delay",
    "manual_note",
    "warning",
    "error",
}


VALID_SEVERITIES = {
    "info",
    "warning",
    "critical",
}


def get_current_time():
    """
    Return the current UTC time as an ISO formatted string.
    """
    return datetime.now(timezone.utc).isoformat()


def check_session_exists(session_id):
    """
    Check if a session exists in the database.

    Args:
        session_id: ID of the session.

    Returns:
        True if the session exists.

    Raises:
        ValueError: If the session does not exist.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM sessions
        WHERE id = ?
        """,
        (session_id,),
    )

    session = cursor.fetchone()
    connection.close()

    if session is None:
        raise ValueError(f"No session found with ID {session_id}.")

    return True


def add_event(session_id, event_type, message="", severity="info", source="manual"):
    """
    Add a manual event to a robot test session.

    Args:
        session_id: ID of the session.
        event_type: Type of event, for example overshoot or sudden_acceleration.
        message: Extra message or note about the event.
        severity: Event severity, for example info, warning, or critical.
        source: Source of the event, for example manual, ROS 2, RWS, or EGM.

    Returns:
        The ID of the created event.
    """
    if not event_type or not event_type.strip():
        raise ValueError("Event type is required.")

    event_type = event_type.strip().lower()
    severity = severity.strip().lower()
    source = source.strip().lower()

    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"Invalid event type '{event_type}'. "
            f"Allowed types: {', '.join(sorted(VALID_EVENT_TYPES))}"
        )

    if severity not in VALID_SEVERITIES:
        raise ValueError(
            f"Invalid severity '{severity}'. "
            f"Allowed severities: {', '.join(sorted(VALID_SEVERITIES))}"
        )

    create_tables()
    check_session_exists(session_id)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO events (
            session_id,
            timestamp,
            event_type,
            message,
            severity,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            get_current_time(),
            event_type,
            message,
            severity,
            source,
        ),
    )

    event_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return event_id


def get_events_for_session(session_id):
    """
    Get all events for one robot test session.

    Args:
        session_id: ID of the session.

    Returns:
        A list of event rows.
    """
    create_tables()
    check_session_exists(session_id)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, session_id, timestamp, event_type, message, severity, source
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """,
        (session_id,),
    )

    events = cursor.fetchall()
    connection.close()

    return events
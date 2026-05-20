import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


DATABASE_PATH = Path("data/magentrace.db")


def get_connection():
    """
    Create and return a connection to the local SQLite database.
    """
    return sqlite3.connect(DATABASE_PATH)


def load_sessions():
    """
    Load all robot test sessions from the database.

    Returns:
        A pandas DataFrame with session data.
    """
    if not DATABASE_PATH.exists():
        return pd.DataFrame()

    connection = get_connection()

    query = """
        SELECT
            id,
            name,
            robot_name,
            software_stack,
            description,
            start_time,
            end_time,
            status
        FROM sessions
        ORDER BY id DESC
    """

    sessions = pd.read_sql_query(query, connection)
    connection.close()

    return sessions


def load_events_for_session(session_id):
    """
    Load all manual events for a selected session.

    Args:
        session_id: ID of the selected session.

    Returns:
        A pandas DataFrame with event data.
    """
    if not DATABASE_PATH.exists():
        return pd.DataFrame()

    connection = get_connection()

    query = """
        SELECT
            id,
            session_id,
            timestamp,
            event_type,
            message,
            severity,
            source
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """

    events = pd.read_sql_query(query, connection, params=(session_id,))
    connection.close()

    return events

def load_joint_states_for_session(session_id):
    """
    Load joint state data for a selected session.
    """
    if not DATABASE_PATH.exists():
        return pd.DataFrame()

    connection = get_connection()

    query = """
        SELECT
            id,
            session_id,
            timestamp,
            joint_name,
            position,
            velocity,
            effort
        FROM joint_states
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """

    joint_states = pd.read_sql_query(query, connection, params=(session_id,))
    connection.close()

    return joint_states

def show_joint_state_chart(joint_states):
    """
    Show a simple joint position chart.
    """
    st.subheader("Joint position chart")

    if joint_states.empty:
        st.warning("No joint state data found for this session yet.")
        return

    chart_data = joint_states.pivot_table(
        index="timestamp",
        columns="joint_name",
        values="position",
        aggfunc="mean",
    )

    st.line_chart(chart_data)


def show_joint_state_table(joint_states):
    """
    Show joint state data as a table.
    """
    st.subheader("Joint state table")

    if joint_states.empty:
        st.write("No joint state data available.")
        return

    st.dataframe(joint_states, use_container_width=True)

def show_session_summary(sessions):
    """
    Show simple summary metrics for all sessions.
    """
    total_sessions = len(sessions)

    active_sessions = len(sessions[sessions["status"] == "active"])
    stopped_sessions = len(sessions[sessions["status"] == "stopped"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total sessions", total_sessions)
    col2.metric("Active sessions", active_sessions)
    col3.metric("Stopped sessions", stopped_sessions)


def show_session_details(session):
    """
    Show details of the selected session.
    """
    st.subheader("Session details")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Session ID:** {session['id']}")
        st.write(f"**Name:** {session['name']}")
        st.write(f"**Robot:** {session['robot_name']}")
        st.write(f"**Status:** {session['status']}")

    with col2:
        st.write(f"**Software stack:** {session['software_stack']}")
        st.write(f"**Start time:** {session['start_time']}")
        st.write(f"**End time:** {session['end_time']}")

    if session["description"]:
        st.write("**Description:**")
        st.info(session["description"])


def show_event_timeline(events):
    """
    Show the event timeline for a selected session.
    """
    st.subheader("Event timeline")

    if events.empty:
        st.warning("No events found for this session yet.")
        return

    for _, event in events.iterrows():
        severity = event["severity"]

        if severity == "critical":
            st.error(
                f"**{event['timestamp']}** — `{event['event_type']}`\n\n"
                f"{event['message']}\n\n"
                f"Source: `{event['source']}`"
            )
        elif severity == "warning":
            st.warning(
                f"**{event['timestamp']}** — `{event['event_type']}`\n\n"
                f"{event['message']}\n\n"
                f"Source: `{event['source']}`"
            )
        else:
            st.info(
                f"**{event['timestamp']}** — `{event['event_type']}`\n\n"
                f"{event['message']}\n\n"
                f"Source: `{event['source']}`"
            )


def show_event_table(events):
    """
    Show event data as a table.
    """
    st.subheader("Event table")

    if events.empty:
        st.write("No event data available.")
        return

    st.dataframe(events, use_container_width=True)


def main():
    """
    Main Streamlit dashboard for the MagenTrace AI prototype.
    """
    st.set_page_config(
        page_title="MagenTrace AI Dashboard",
        page_icon="🤖",
        layout="wide",
    )

    st.title("MagenTrace AI")
    st.caption("Robot flight recorder prototype for session-based safety analysis")

    sessions = load_sessions()

    if sessions.empty:
        st.warning(
            "No sessions found. Start a session first by using the CLI command."
        )

        st.code(
            'python -m backend.main start "Large joint movement test" '
            '--robot "ABB GoFa" '
            '--software "ROS 2 + MoveIt2 + EGM" '
            '--description "Testing abnormal movement behaviour"',
            language="powershell",
        )
        return

    show_session_summary(sessions)

    st.divider()

    st.subheader("Sessions")

    session_options = {
        f"{row['id']} - {row['name']} ({row['status']})": row["id"]
        for _, row in sessions.iterrows()
    }

    selected_label = st.selectbox(
        "Select a session",
        options=list(session_options.keys()),
    )

    selected_session_id = session_options[selected_label]

    selected_session = sessions[sessions["id"] == selected_session_id].iloc[0]

    show_session_details(selected_session)

    st.divider()

    events = load_events_for_session(selected_session_id)

    show_event_timeline(events)

    st.divider()

    show_event_table(events)

    st.divider()

    joint_states = load_joint_states_for_session(selected_session_id)

    show_joint_state_chart(joint_states)

    st.divider()

    show_joint_state_table(joint_states)

if __name__ == "__main__":
    main()
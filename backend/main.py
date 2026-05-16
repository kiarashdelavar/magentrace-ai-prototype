import argparse

from backend.session_service import (
    start_session,
    stop_session,
    get_all_sessions,
    get_active_session,
)

from backend.event_service import add_event, get_events_for_session


def print_sessions(sessions):
    """
    Print sessions in a simple readable format.
    """
    if not sessions:
        print("No sessions found.")
        return

    for session in sessions:
        print("-" * 60)
        print(f"ID: {session[0]}")
        print(f"Name: {session[1]}")
        print(f"Robot: {session[2]}")
        print(f"Software stack: {session[3]}")
        print(f"Description: {session[4]}")
        print(f"Start time: {session[5]}")
        print(f"End time: {session[6]}")
        print(f"Status: {session[7]}")


def print_events(events):
    """
    Print events in a simple readable format.
    """
    if not events:
        print("No events found for this session.")
        return

    for event in events:
        print("-" * 60)
        print(f"ID: {event[0]}")
        print(f"Session ID: {event[1]}")
        print(f"Timestamp: {event[2]}")
        print(f"Event type: {event[3]}")
        print(f"Message: {event[4]}")
        print(f"Severity: {event[5]}")
        print(f"Source: {event[6]}")


def main():
    """
    Simple command line interface for testing session and event logging.
    """
    parser = argparse.ArgumentParser(
        description="MagenTrace AI robot session logger"
    )

    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start", help="Start a new robot test session")
    start_parser.add_argument("name", help="Name of the session")
    start_parser.add_argument("--robot", default="ABB GoFa", help="Robot name")
    start_parser.add_argument(
        "--software",
        default="ROS 2 + MoveIt2 + ABB EGM",
        help="Software stack used in the session",
    )
    start_parser.add_argument(
        "--description",
        default="",
        help="Short description of the test session",
    )

    stop_parser = subparsers.add_parser("stop", help="Stop an active robot test session")
    stop_parser.add_argument("session_id", type=int, help="ID of the session to stop")

    event_parser = subparsers.add_parser(
        "event",
        help="Add a manual event to a session",
    )
    event_parser.add_argument("session_id", type=int, help="ID of the session")
    event_parser.add_argument(
        "event_type",
        help="Event type, for example overshoot, sudden_acceleration, unexpected_stop, delay, or manual_note",
    )
    event_parser.add_argument(
        "message",
        help="Message or note about the event",
    )
    event_parser.add_argument(
        "--severity",
        default="info",
        help="Event severity: info, warning, or critical",
    )
    event_parser.add_argument(
        "--source",
        default="manual",
        help="Event source, for example manual, ROS 2, RWS, or EGM",
    )

    events_parser = subparsers.add_parser(
        "events",
        help="List events for a session",
    )
    events_parser.add_argument("session_id", type=int, help="ID of the session")

    subparsers.add_parser("list", help="List all sessions")
    subparsers.add_parser("active", help="Show the latest active session")

    args = parser.parse_args()

    if args.command == "start":
        session_id = start_session(
            name=args.name,
            robot_name=args.robot,
            software_stack=args.software,
            description=args.description,
        )
        print(f"Started session with ID: {session_id}")

    elif args.command == "stop":
        stop_session(args.session_id)
        print(f"Stopped session with ID: {args.session_id}")

    elif args.command == "event":
        event_id = add_event(
            session_id=args.session_id,
            event_type=args.event_type,
            message=args.message,
            severity=args.severity,
            source=args.source,
        )
        print(f"Added event with ID: {event_id}")

    elif args.command == "events":
        events = get_events_for_session(args.session_id)
        print_events(events)

    elif args.command == "list":
        sessions = get_all_sessions()
        print_sessions(sessions)

    elif args.command == "active":
        session = get_active_session()
        if session is None:
            print("No active session found.")
        else:
            print_sessions([session])

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
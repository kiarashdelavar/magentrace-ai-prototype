import argparse

from backend.session_service import (
    start_session,
    stop_session,
    get_all_sessions,
    get_active_session,
)


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


def main():
    """
    Simple command line interface for testing session logging.
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
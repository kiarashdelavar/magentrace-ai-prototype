import random
import time

from backend.joint_state_service import add_joint_state


JOINT_NAMES = [
    "joint_1",
    "joint_2",
    "joint_3",
    "joint_4",
    "joint_5",
    "joint_6",
]


def generate_mock_joint_data(session_id, samples=10, delay_seconds=0.2):
    """
    Generate fake joint state data for testing without ROS 2.
    """
    for sample_index in range(samples):
        for joint_name in JOINT_NAMES:
            position = round(random.uniform(-3.14, 3.14), 4)
            velocity = round(random.uniform(-1.5, 1.5), 4)
            effort = round(random.uniform(0.0, 20.0), 4)

            add_joint_state(
                session_id=session_id,
                joint_name=joint_name,
                position=position,
                velocity=velocity,
                effort=effort,
            )

        print(f"Saved mock joint sample {sample_index + 1}/{samples}")
        time.sleep(delay_seconds)


if __name__ == "__main__":
    session_id_input = int(input("Enter session ID: "))
    generate_mock_joint_data(session_id=session_id_input)
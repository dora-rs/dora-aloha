"""
Dynamixel Client: This node is used to represent a chain of dynamixel motors. It can be used to read positions,
velocities, currents, and set goal positions and currents.
"""

import os
import argparse

import numpy as np
import pyarrow as pa

from dora import Node

from dynamixel import DynamixelXLBus, TorqueMode, retrieve_ids_and_command, u32_to_i32, i32_to_u32


def apply_homing_offset(values: np.array, homing_offset: np.array) -> np.array:
    """
    Apply the homing offset to the values.
    values: np.array of i32
    """

    for i in range(len(values)):
        if values[i] is not None:
            values[i] += homing_offset[i]

    return values


def apply_inverted(values: np.array, inverted: np.array) -> np.array:
    """
    Apply the inverted values.
    values: np.array of i32
    """

    for i in range(len(values)):
        if values[i] is not None and inverted[i]:
            values[i] = -values[i]

    return values


def apply_configuration(values: np.array, homing_offset: np.array, inverted: np.array) -> np.array:
    """
    Get the working position of the robot
    Args:
        values: 
        homing_offset: 
        inverted: 

    Returns:

    """

    return apply_homing_offset(apply_inverted(values, inverted), homing_offset)


def invert_configuration(values: np.array, homing_offset: np.array, inverted: np.array) -> np.array:
    """
    Transform working position into real position for the robot.
    Args:
        values: 
        homing_offset: 
        inverted: 

    Returns:

    """

    return apply_inverted(apply_homing_offset(values, np.array([
        -offset if offset is not None else None for offset in homing_offset
    ])), inverted)


class Client:

    def __init__(self, config):
        self.config = config
        self.chain = DynamixelXLBus(config["port"], config["ids"])

        self.homing_offset = config["homing_offset"]
        self.inverted = config["inverted"]

        # Set initial values

        try:
            self.chain.sync_write_torque_enable(config["torque"])
        except Exception as e:
            print("Error writing torque status:", e)

        try:
            positions = invert_configuration(
                config["initial_goal_position"],
                self.homing_offset,
                self.inverted)

            ids, positions = retrieve_ids_and_command(positions, self.chain.motor_ids)

            self.chain.sync_write_goal_position_i32(positions, ids)
        except Exception as e:
            print("Error writing goal position:", e)

        try:
            ids, currents = retrieve_ids_and_command(
                config["initial_goal_current"],
                self.chain.motor_ids)

            self.chain.sync_write_goal_current(currents, ids)
        except Exception as e:
            print("Error writing goal current:", e)

        # Create node and connect it to dataflow (if dynamic)

        self.node = Node(config["name"])

        self.pull_present_position(self.node, None)

    def run(self):
        # Run the event loop of Dora and call appropriate functions

        for event in self.node:
            event_type = event["type"]

            if event_type == "INPUT":
                event_id = event["id"]

                if event_id == "pull_present_position":
                    self.pull_present_position(self.node, event["metadata"])
                elif event_id == "pull_goal_position":
                    self.pull_goal_position(self.node, event["metadata"])
                elif event_id == "pull_present_velocity":
                    self.pull_present_velocity(self.node, event["metadata"])
                elif event_id == "write_goal_position":
                    self.write_goal_position(event["value"])
                elif event_id == "write_goal_current":
                    self.write_goal_current(event["value"])
                elif event_id == "write_goal_velocity":
                    self.write_goal_velocity(event["value"])

            elif event_type == "STOP":
                break
            elif event_type == "ERROR":
                raise ValueError("An error occurred in the dataflow: " + event["error"])

    def close(self):
        self.chain.sync_write_torque_enable(TorqueMode.DISABLED.value)
        self.chain.close()

    def pull_present_position(self, node, metadata):
        try:
            position = i32_to_u32(apply_configuration(
                self.chain.sync_read_present_position_i32(),
                self.homing_offset,
                self.inverted))

            node.send_output(
                "present_position",
                pa.array(position.ravel()),
                metadata
            )

        except ConnectionError as e:
            print("Error reading position:", e)

    def pull_goal_position(self, node, metadata):
        try:
            goal_position = i32_to_u32(apply_configuration(
                self.chain.sync_read_goal_position_i32(),
                self.homing_offset,
                self.inverted))

            node.send_output(
                "goal_position",
                pa.array(goal_position.ravel()),
                metadata
            )
        except ConnectionError as e:
            print("Error reading goal position:", e)

    def pull_present_velocity(self, node, metadata):
        try:
            velocity = self.chain.sync_read_present_velocity()

            node.send_output(
                "present_velocity",
                pa.array(velocity.ravel()),
                metadata
            )
        except ConnectionError as e:
            print("Error reading velocity:", e)

    def write_goal_position(self, goal_position):
        try:
            positions = invert_configuration(u32_to_i32(goal_position).to_numpy().copy(),
                                             self.homing_offset,
                                             self.inverted)

            ids, positions = retrieve_ids_and_command(positions, self.chain.motor_ids)

            self.chain.sync_write_goal_position_i32(positions, ids)
        except ConnectionError as e:
            print("Error writing goal position:", e)

    def write_goal_current(self, goal_current):
        try:
            ids, currents = retrieve_ids_and_command(
                goal_current,
                self.chain.motor_ids)

            self.chain.sync_write_goal_current(currents, ids)
        except ConnectionError as e:
            print("Error writing goal current:", e)

    def write_goal_velocity(self, goal_velocity):
        try:
            ids, velocities = retrieve_ids_and_command(
                goal_velocity,
                self.chain.motor_ids)

            self.chain.sync_write_goal_velocity(velocities, ids)
        except ConnectionError as e:
            print("Error writing goal velocity:", e)


def main():
    # Handle dynamic nodes, ask for the name of the node in the dataflow
    parser = argparse.ArgumentParser(
        description="Dynamixel Client: This node is used to represent a chain of dynamixel motors. "
                    "It can be used to read "
                    "positions, velocities, currents, and set goal positions and currents.")

    parser.add_argument("--name", type=str, required=False, help="The name of the node in the dataflow.",
                        default="dynamixel_client")

    args = parser.parse_args()

    # Check if port is set
    if not os.environ.get("PORT"):
        raise ValueError("The port is not set. Please set the port of the dynamixel motors.")

    # Create configuration
    config = {
        "name": args.name,
        "port": os.environ.get("PORT"),  # (e.g. "/dev/ttyUSB0", "COM3")
        "ids": list(map(int, os.environ.get("IDS", "1 2 3 4 5 6").split())),
        "torque": [1 if value == "True" else 0 for value in
                   list(os.getenv("TORQUE", "True True True True True True").split())],

        "initial_goal_position": [int(value) if 'None' not in value else None for value in
                                  list(os.getenv("INITIAL_GOAL_POSITION", "None None None None None None").split())],
        "initial_goal_current": [int(value) if 'None' not in value else None for value in
                                 list(os.getenv("INITIAL_GOAL_CURRENT", "None None None None None None").split())],

        "homing_offset": list(map(int, os.environ.get("HOMING_OFFSET", "0, 0, 0, 0, 0, 0").split())),
        "inverted": [True if value == "True" else False for value in
                     list(os.getenv("INVERTED", "False False False False False False").split())]
    }

    print("Dynamixel Client Configuration: ", config, flush=True)

    client = Client(config)
    client.run()
    client.close()


if __name__ == '__main__':
    main()

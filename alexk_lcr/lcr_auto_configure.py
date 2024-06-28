"""
LCR Auto Configure: This program is used to automatically configure the Low Cost Robot (LCR) for the user.

The program will:
1. Disable all torque motors of provided LCR.
2. Ask the user to move the LCR to the position 1 (see CONFIGURING.md for more details).
3. Record the position of the LCR.
4. Ask the user to move the LCR to the position 2 (see CONFIGURING.md for more details).
5. Record the position of the LCR.
8. Calculate the offset of the LCR and save it to the configuration file.

It will also enable all appropriate operating modes for the LCR.
"""

import argparse
import time

import numpy as np

from dynamixel import DynamixelXLMotorsChain, OperatingMode, DriveMode


def pause():
    """
    Pause the program until the user presses the enter key.
    """
    input("Press Enter to continue...")


def i32_to_u32(value: np.array) -> np.array:
    for i in range(len(value)):
        if value[i] is not None and value[i] < 0:
            value[i] = value[i] + 4294967296

    return value


def u32_to_i32(value: np.array) -> np.array:
    for i in range(len(value)):
        if value[i] is not None and value[i] > 2147483647:
            value[i] = value[i] - 4294967296

    return value


def apply_homing_offset(values: np.array, homing_offset: np.array) -> np.array:
    values = u32_to_i32(values)

    for i in range(len(values)):
        if values[i] is not None:
            values[i] += homing_offset[i]

    return i32_to_u32(values)


def apply_inverted(values: np.array, inverted: np.array) -> np.array:
    values = u32_to_i32(values)

    for i in range(len(values)):
        if values[i] is not None and inverted[i]:
            values[i] = -values[i]

    return i32_to_u32(values)


def apply_configuration(values: np.array, homing_offset: np.array, inverted: np.array) -> np.array:
    return apply_homing_offset(apply_inverted(values, inverted), homing_offset)


def read_present_positions(arm: DynamixelXLMotorsChain) -> np.array:
    """
    Read the present positions of the motors.
    :param arm: DynamixelXLMotorsChain
    :return: numpy array of present positions
    """
    try:

        present_positions = arm.sync_read_present_position()
    except ConnectionError as e:
        print("Error while reading present positions: ", e)

        return np.array([None, None, None, None, None, None])

    return present_positions


def prepare_configuration(arm: DynamixelXLMotorsChain):
    """
    Prepare the configuration for the LCR.
    :param arm: DynamixelXLMotorsChain
    """

    # To be configured, all servos must be in "torque disable" mode
    arm.sync_write_torque_enable(0)

    # We need to work with 'extended position mode' (4) for all servos, because in joint mode (1) the servos can't
    # rotate more than 360 degrees (from 0 to 4095) And some mistake can happen while assembling the arm,
    # you could end up with a servo with a position 0 or 4095 at a crucial point See [
    # https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/#operating-mode11]
    arm.sync_write_operating_mode(OperatingMode.EXTENDED_POSITION.value, [1, 2, 3, 4, 5])

    # Gripper is always 'position control current based' (5)
    arm.write_operating_mode(OperatingMode.CURRENT_CONTROLLED_POSITION.value, 6)

    # We need to reset the homing offset for all servos
    arm.sync_write_homing_offset(0)

    # We need to work with 'normal drive mode' (0) for all servos
    arm.sync_write_drive_mode(DriveMode.NON_INVERTED.value)


def invert_appropriate_positions(positions: np.array, inverted: list[bool]) -> np.array:
    """
    Invert the appropriate positions.
    :param positions: numpy array of positions
    :param inverted: list of booleans to determine if the position should be inverted
    :return: numpy array of inverted positions
    """
    for i, invert in enumerate(inverted):
        if not invert and positions[i] is not None:
            positions[i] = -positions[i]

    return positions


def calculate_corrections(positions: np.array, inverted: list[bool], wanted: np.array) -> np.array:
    """
    Calculate the corrections for the positions.
    :param positions: numpy array of positions
    :param inverted: list of booleans to determine if the position should be inverted
    :param wanted: numpy array of wanted positions
    :return: numpy array of corrections
    """

    correction = invert_appropriate_positions(positions, inverted)

    for i in range(len(positions)):
        if correction[i] is not None:
            if inverted[i]:
                correction[i] -= wanted[i]
            else:
                correction[i] += wanted[i]

    return correction


def calculate_nearest_rounded_positions(positions: np.array) -> np.array:
    """
    Calculate the nearest rounded positions.
    :param positions: numpy array of positions
    :return: numpy array of nearest rounded positions
    """

    return np.array(
        [round(positions[i] / 1024) * 1024 if positions[i] is not None else None for i in range(len(positions))])


def configure_homing(arm: DynamixelXLMotorsChain, inverted: list[bool], wanted: np.array) -> np.array:
    """
    Configure the homing for the LCR.
    :param arm: DynamixelXLMotorsChain
    :param inverted: list of booleans to determine if the position should be inverted
    """

    # Get the present positions of the servos
    present_positions = u32_to_i32(
        apply_configuration(read_present_positions(arm), np.array([0, 0, 0, 0, 0, 0]), inverted))

    nearest_positions = calculate_nearest_rounded_positions(present_positions)

    correction = calculate_corrections(nearest_positions, inverted, wanted)

    return correction


def configure_drive_mode(arm: DynamixelXLMotorsChain, homing: np.array):
    """
    Configure the drive mode for the LCR.
    :param arm: DynamixelXLMotorsChain
    :param homing: numpy array of homing
    """
    # Get current positions
    present_positions = u32_to_i32(
        apply_configuration(read_present_positions(arm), homing, np.array([False, False, False, False, False, False])))

    nearest_positions = calculate_nearest_rounded_positions(present_positions)

    # construct 'inverted' list comparing nearest_positions and wanted_position_2
    inverted = []

    for i in range(len(nearest_positions)):
        inverted.append(nearest_positions[i] != wanted_position_2()[i])

    return inverted


def wanted_position_1() -> np.array:
    """
    The present position wanted in position 1 for the arm
    """
    return np.array([0, -1024, 1024, 0, 0, 0])


def wanted_position_2() -> np.array:
    """
    The present position wanted in position 2 for the arm
    """
    return np.array([1024, 0, 0, 1024, 1024, -1024])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LCR Auto Configure: This program is used to automatically configure the Low Cost Robot (LCR) for "
                    "the user.")

    parser.add_argument("--port", type=str, required=True, help="The port of the LCR.")

    args = parser.parse_args()

    arm = DynamixelXLMotorsChain(args.port, [1, 2, 3, 4, 5, 6])

    prepare_configuration(arm)

    # Ask the user to move the LCR to the position 1
    print("Please move the LCR to the position 1")
    pause()

    homing = configure_homing(arm, [False, False, False, False, False, False], wanted_position_1())

    # Ask the user to move the LCR to the position 2
    print("Please move the LCR to the position 2")
    pause()

    inverted = configure_drive_mode(arm, homing)
    homing = configure_homing(arm, inverted, wanted_position_2())

    for i in range(len(inverted)):
        if inverted[i]:
            homing[i] = -homing[i]

    print("Configuration done!")

    print("Here is the configuration: ")

    print("HOMING_OFFSET: ", " ".join([str(i) for i in homing]))
    print("INVERTED: ", " ".join([str(i) for i in inverted]))

    print("Make sure everything is working properly:")

    while True:
        positions = apply_configuration(read_present_positions(arm), homing, inverted)
        print(u32_to_i32(positions))

        time.sleep(1)
"""
Copy of Lerobot/common files waiting for a release build of this
"""

from copy import deepcopy
import enum
import numpy as np

from dynamixel_sdk import PacketHandler, PortHandler, COMM_SUCCESS, GroupSyncRead, GroupSyncWrite
from dynamixel_sdk import DXL_HIBYTE, DXL_HIWORD, DXL_LOBYTE, DXL_LOWORD

PROTOCOL_VERSION = 2.0
BAUDRATE = 1_000_000
TIMOUT_MS = 1000


class TorqueMode(enum.Enum):
    ENABLED = 1
    DISABLED = 0


class OperatingMode(enum.Enum):
    VELOCITY = 1
    POSITION = 3
    EXTENDED_POSITION = 4
    CURRENT_CONTROLLED_POSITION = 5
    PWM = 16
    UNKNOWN = -1


class DriveMode(enum.Enum):
    NON_INVERTED = 0
    INVERTED = 1


# https://emanual.robotis.com/docs/en/dxl/x/xl330-m077
# https://emanual.robotis.com/docs/en/dxl/x/xl330-m288
# https://emanual.robotis.com/docs/en/dxl/x/xl430-w250
# https://emanual.robotis.com/docs/en/dxl/x/xm430-w350
# https://emanual.robotis.com/docs/en/dxl/x/xm540-w270

# data_name, address, size (byte)
X_SERIE_CONTROL_TABLE = [
    ("goal_position", 116, 4),
    ("goal_current", 102, 2),
    ("goal_pwm", 100, 2),
    ("goal_velocity", 104, 4),
    ("position", 132, 4),
    ("current", 126, 2),
    ("pwm", 124, 2),
    ("velocity", 128, 4),
    ("torque", 64, 1),
    ("temperature", 146, 1),
    ("temperature_limit", 31, 1),
    ("pwm_limit", 36, 2),
    ("current_limit", 38, 2),
]

MODEL_CONTROL_TABLE = {
    "xl330-m077": X_SERIE_CONTROL_TABLE,
    "xl330-m288": X_SERIE_CONTROL_TABLE,
    "xl430-w250": X_SERIE_CONTROL_TABLE,
    "xm430-w350": X_SERIE_CONTROL_TABLE,
    "xm540-w270": X_SERIE_CONTROL_TABLE,
}


class DynamixelXLMotorsChain:

    def __init__(self, port: str, motor_models: dict[int, str],
                 extra_model_control_table: dict[str, list[tuple]] | None = None):
        self.port = port
        self.motor_models = motor_models

        self.model_ctrl_table = deepcopy(MODEL_CONTROL_TABLE)
        if extra_model_control_table:
            self.model_ctrl_table.update(extra_model_control_table)

        # Find read/write addresses and number of bytes for each motor
        self.motor_ctrl = {}
        for idx, model in self.motor_models.items():
            for data_name, addr, bytes in self.model_ctrl_table[model]:
                if idx not in self.motor_ctrl:
                    self.motor_ctrl[idx] = {}
                self.motor_ctrl[idx][data_name] = {
                    "addr": addr,
                    "bytes": bytes,
                }

        self.port_handler = PortHandler(self.port)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)

        if not self.port_handler.openPort():
            raise OSError(f"Failed to open port {self.port}")

        if not self.port_handler.setBaudRate(BAUDRATE):
            raise OSError(f"Failed to set baudrate to {BAUDRATE}")

        if not self.port_handler.setPacketTimeoutMillis(TIMOUT_MS):
            raise OSError(f"Failed to set packet timeout to {TIMOUT_MS} (ms)")

        self.group_readers = {}
        self.group_writers = {}

    @property
    def motor_ids(self) -> list[int]:
        return list(self.motor_models.keys())

    def write(self, data_name, value, motor_idx: int):

        addr = self.motor_ctrl[motor_idx][data_name]["addr"]
        bytes = self.motor_ctrl[motor_idx][data_name]["bytes"]
        args = (self.port_handler, motor_idx, addr, value)
        if bytes == 1:
            comm, err = self.packet_handler.write1ByteTxRx(*args)
        elif bytes == 2:
            comm, err = self.packet_handler.write2ByteTxRx(*args)
        elif bytes == 4:
            comm, err = self.packet_handler.write4ByteTxRx(*args)
        else:
            raise NotImplementedError(
                f"Value of the number of bytes to be sent is expected to be in [1, 2, 4], but {bytes} "
                f"is provided instead.")

        if comm != COMM_SUCCESS:
            raise ConnectionError(
                f"Write failed due to communication error on port {self.port} for motor {motor_idx}: "
                f"{self.packet_handler.getTxRxResult(comm)}"
            )
        elif err != 0:
            raise ConnectionError(
                f"Write failed due to error {err} on port {self.port} for motor {motor_idx}: "
                f"{self.packet_handler.getTxRxResult(err)}"
            )

    def read(self, data_name, motor_idx: int):
        addr = self.motor_ctrl[motor_idx][data_name]["addr"]
        bytes = self.motor_ctrl[motor_idx][data_name]["bytes"]
        args = (self.port_handler, motor_idx, addr)
        if bytes == 1:
            value, comm, err = self.packet_handler.read1ByteTxRx(*args)
        elif bytes == 2:
            value, comm, err = self.packet_handler.read2ByteTxRx(*args)
        elif bytes == 4:
            value, comm, err = self.packet_handler.read4ByteTxRx(*args)
        else:
            raise NotImplementedError(
                f"Value of the number of bytes to be sent is expected to be in [1, 2, 4], but "
                f"{bytes} is provided instead.")

        if comm != COMM_SUCCESS:
            raise ConnectionError(
                f"Read failed due to communication error on port {self.port} for motor {motor_idx}: "
                f"{self.packet_handler.getTxRxResult(comm)}"
            )
        elif err != 0:
            raise ConnectionError(
                f"Read failed due to error {err} on port {self.port} for motor {motor_idx}: "
                f"{self.packet_handler.getTxRxResult(err)}"
            )

        return value

    def sync_read(self, data_name, motor_ids: list[int] | None = None):
        if motor_ids is None:
            motor_ids = self.motor_ids

        group_key = f"{data_name}_" + "_".join([str(idx) for idx in motor_ids])
        first_motor_idx = list(self.motor_ctrl.keys())[0]
        addr = self.motor_ctrl[first_motor_idx][data_name]["addr"]
        bytes = self.motor_ctrl[first_motor_idx][data_name]["bytes"]

        if data_name not in self.group_readers:
            self.group_readers[group_key] = GroupSyncRead(self.port_handler, self.packet_handler, addr, bytes)
            for idx in motor_ids:
                self.group_readers[group_key].addParam(idx)

        comm = self.group_readers[group_key].txRxPacket()
        if comm != COMM_SUCCESS:
            raise ConnectionError(
                f"Read failed due to communication error on port {self.port} for group_key {group_key}: "
                f"{self.packet_handler.getTxRxResult(comm)}"
            )

        values = []
        for idx in motor_ids:
            value = self.group_readers[group_key].getData(idx, addr, bytes)
            values.append(value)

        return np.array(values)

    def sync_write(self, data_name, values: int | list[int], motor_ids: int | list[int] | None = None):
        if motor_ids is None:
            motor_ids = self.motor_ids

        if isinstance(motor_ids, int):
            motor_ids = [motor_ids]

        if isinstance(values, (int, np.integer)):
            values = [int(values)] * len(motor_ids)

        if isinstance(values, np.ndarray):
            values = values.tolist()

        group_key = f"{data_name}_" + "_".join([str(idx) for idx in motor_ids])

        first_motor_idx = list(self.motor_ctrl.keys())[0]
        addr = self.motor_ctrl[first_motor_idx][data_name]["addr"]
        bytes = self.motor_ctrl[first_motor_idx][data_name]["bytes"]
        init_group = data_name not in self.group_readers

        if init_group:
            self.group_writers[group_key] = GroupSyncWrite(self.port_handler, self.packet_handler, addr, bytes)

        for idx, value in zip(motor_ids, values):
            if bytes == 1:
                data = [
                    DXL_LOBYTE(DXL_LOWORD(value)),
                ]
            elif bytes == 2:
                data = [
                    DXL_LOBYTE(DXL_LOWORD(value)),
                    DXL_HIBYTE(DXL_LOWORD(value)),
                ]
            elif bytes == 4:
                data = [
                    DXL_LOBYTE(DXL_LOWORD(value)),
                    DXL_HIBYTE(DXL_LOWORD(value)),
                    DXL_LOBYTE(DXL_HIWORD(value)),
                    DXL_HIBYTE(DXL_HIWORD(value)),
                ]

            if init_group:
                self.group_writers[group_key].addParam(idx, data)
            else:
                self.group_writers[group_key].changeParam(idx, data)

        self.group_writers[group_key].txPacket()

    def write_torque_enable(self, motor_idx: int):
        self.write("torque", TorqueMode.ENABLED.value, motor_idx)

    def write_torque_disable(self, motor_idx: int):
        self.write("torque", TorqueMode.DISABLED.value, motor_idx)

    def write_operating_mode(self, mode: OperatingMode, motor_idx: int):
        self.write("torque", mode, motor_idx)

    def read_position(self, motor_idx: int):
        return self.read("position", motor_idx)

    def write_goal_position(self, value, motor_idx: int):
        self.write("goal_position", value, motor_idx)

    def sync_torque_enable(self, motor_ids: list[int] | None = None):
        if motor_ids is None:
            motor_ids = self.motor_ids

        self.sync_write("torque", TorqueMode.ENABLED.value, motor_ids)

    def sync_torque_disable(self, motor_ids: list[int] | None = None):
        if motor_ids is None:
            motor_ids = self.motor_ids
        self.sync_write("torque", TorqueMode.DISABLED.value, motor_ids)

    def sync_write_operating_mode(self, mode: OperatingMode, motor_ids: list[int] | None = None):
        if motor_ids is None:
            motor_ids = self.motor_ids

        self.sync_write("torque", [mode.value] * len(motor_ids), motor_ids)

    def sync_read_position(self, motor_ids: list[int] | None = None):
        if motor_ids is None:
            motor_ids = self.motor_ids

        return self.sync_read("position", motor_ids)

    def sync_write_goal_position(self, values, motor_ids: list[int] | None = None):
        if motor_ids is None:
            motor_ids = self.motor_ids

        self.sync_write("goal_position", values, motor_ids)

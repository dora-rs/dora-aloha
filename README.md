# `dora-rs` powered ALOHA

## Teleop Getting started

```bash
sudo apt install libudev-dev

cargo run -p aloha-teleop --release
```

### Hardware Installation

- To check if the robot is connected, install dynamixel wizard [here](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/)
- Dynamixel wizard is a very helpful debugging tool that connects to individual motors of the robot. It allows
  things such as rebooting the motor (very useful!), torque on/off, and sending commands.
  However, it has no knowledge about the kinematics of the robot, so be careful about collisions.
  The robot _will_ collapse if motors are torque off i.e. there is no automatically engaged brakes in joints.
- Open Dynamixel wizard, go into `options` and select:
  - Protocal 2.0
  - All ports
  - 1000000 bps
  - ID range from 0-10
- Note: repeat above everytime before you scan.
- Then hit `Scan`. There should be 4 devices showing up, each with 9 motors.
- One issue that arises is the port each robot binds to can change over time, e.g. a robot that
  is initially `ttyUSB0` might suddenly become `ttyUSB5`. To resolve this, we bind each robot to a fixed symlink
  port with the following mapping:
  - `ttyDXL_master_right`: right master robot (master: the robot that the operator would be holding)
  - `ttyDXL_puppet_right`: right puppet robot (puppet: the robot that performs the task)
  - `ttyDXL_master_left`: left master robot
  - `ttyDXL_puppet_left`: left puppet robot
- Take `ttyDXL_master_right`: right master robot as an example:

  1. Find the port that the right master robot is currently binding to, e.g. `ttyUSB0`
  2. run `udevadm info --name=/dev/ttyUSB0 --attribute-walk | grep serial` to obtain the serial number. Use the first one that shows up, the format should look similar to `FT6S4DSP`.
  3. `sudo vim /etc/udev/rules.d/99-fixed-interbotix-udev.rules` and add the following line:

     SUBSYSTEM=="tty", ATTRS{serial}=="<serial number here>", ENV{ID_MM_DEVICE_IGNORE}="1", ATTR{device/latency_timer}="1", SYMLINK+="ttyDXL_master_right"

  4. This will make sure the right master robot is _always_ binding to `ttyDXL_master_right`
  5. Repeat with the rest of 3 arms.

> You have an example of the given rules in `hardware_config.yml`.

```bash
sudo cp hardware_config/99-interbotix-udev.rules /etc/udev/rules.d
sudo cp hardware_config/99-fixed-interbotix-udev.rules /etc/udev/rules.d
```

- To apply the changes, run `sudo udevadm control --reload && sudo udevadm trigger`
- If successful, you should be able to find `ttyDXL*` in your `/dev`

## Hardware troubleshoot

- In case you're having `xsarm_control.launch.py` that is not launching for the reason: ` Can't find Dynamixel ID 'X'`, one of the issue I faced in my demo was Overload Error(OL). The fix was to go on Dynamixel Wizard, click on the motor ID `X` and clicking the reboot button the right side of the window. This error happens when the torque is too high. I had the issue when I try to set a closing position for the gripper that did not take into account the fingers.

## Support Matrix

This application should be cross-platformed: Linux, Windows, MacOS.

Please raise an issue if not.

## Documentation

https://github.com/Interbotix/interbotix_ros_toolboxes/blob/humble/interbotix_xs_toolbox/interbotix_xs_modules/interbotix_xs_modules/xs_robot/core.py
https://github.com/Interbotix/interbotix_ros_toolboxes/blob/c187bcea89b60391244bb19943ebd78f770aa975/interbotix_xs_toolbox/interbotix_xs_modules/interbotix_xs_modules/xs_robot/core.py#L380-L398

## Acknowledgement

This work is heavily inspired from [tonyzhaozh/aloha](https://github.com/tonyzhaozh/aloha) and we're trying to bring perfornance improvement.

# Dora pipeline for teleoperated low-cost arm and episode recording for LeRobot

AlexK Low Cost Robot is a low-cost robotic arm that can be teleoperated using a similar arm. This repository contains
the Dora pipeline to record episodes for LeRobot.

## Assembling

Check the [ASSEMBLING.md](ASSEMBLING.md) file for instructions on how to assemble the robot from scratch using the
provided parts from the [AlexK Low Cost Robot](https://github.com/AlexanderKoch-Koch/low_cost_robot)

## Installations

Check the [INSTALLATIONS.md](INSTALLATION.md) file for instructions on how to install the required software and
environment
to run the robot.

## Configuring

Check the [CONFIGURING.md](CONFIGURING.md) file for instructions on how to configure the robot to record episodes for
LeRobot and teleoperate the robot.

## Recording

This section is under construction.

## Examples

There are also some other example applications in the `graph` folder. Have fun!

Here is a list of the available examples:

- `mono_teleop.yml`: A simple teleoperation pipeline that allows you to control a follower arm using a leader arm. It
  does not record the episodes, so you don't need to have a camera.

You must configure the arms, retrieve the device port, and modify the file `mono_teleop.yml` to set the correct
environment variables. (e.g. `PORT`, `HOMING_OFFSETS`, `INVERTED`)

```bash
cd dora-lerobot/alexk_lcr

# If you are using a custom environment, you will have to activate it before running the command
source [your_custom_env_bin]/activate

# If you followed the installation instructions, you can run the following command
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell

dora up
dora start ./graphs/mono_teleop.yml
```

- `bi_teleop.yml`: A simple teleoperation pipeline that allows you to control two follower arm using two leader arm
  (left and right). It does not record the episodes, so you don't need to have a camera.

You must configure the arms, retrieve the device port, and modify the file `bi_teleop.yml` to set the correct
environment variables. (e.g. `PORT`, `HOMING_OFFSETS`, `INVERTED`)

```bash
cd dora-lerobot/alexk_lcr

# If you are using a custom environment, you will have to activate it before running the command
source [your_custom_env_bin]/activate

# If you followed the installation instructions, you can run the following command
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell

dora up
dora start ./graphs/bi_teleop.yml
```

## License

This library is licensed under the [Apache License 2.0](../LICENSE).

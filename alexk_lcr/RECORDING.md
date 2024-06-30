# Dora pipeline for teleoperated low-cost arm and episode recording for LeRobot

AlexK Low Cost Robot is a low-cost robotic arm that can be teleoperated using a similar arm. This repository contains
the Dora pipeline to manipulate the arms, the camera, and record/replay episodes with LeRobot.

## Recording

A Dora application is described by a graph file. The graph file is a YAML file that describes the nodes, the inputs, and
the outputs of the nodes. The graph file is used to create a Dora pipeline that can be run on a computer.

The first thing to do is configuring the Dora graph to integrate the arms and the camera. The graph file is located in
the `graphs` folder. The graph file is named `record_teleop.yml`.

Those are the the steps to teleoperate the arm and record the episodes:

- adjust the serial ports for the master and puppet arms as env variables
  in : `MASTER_PATH`, `PUPPET_PATH`, `CAMERA_ID`

- Open a terminal and navigate to the root of the submodule `alexk_lcr` in the repository.

```bash
cd dora-lerobot/alexk_lcr
```

- Start your Dora application with the following command:

```bash
# If you are using a custom environment, you will have to activate it before running the command
source [your_custom_env_bin]/activate

# If you followed the installation instructions, you can run the following command
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell

dora up
dora start ./graphs/record_teleop.yml
```

Then, you can teleoperate the arm by using the master arm, and record the episodes:

1. Press space to move to the next episode and save the previous one
2. Press esc when finished with all
3. Pressing backspace will end the current episode, save it and wait until space is pressed to start a new episode
4. After having pressed esc, type `dora stop` to stop the Dora pipeline.
5. Write down the location of the logs (e.g `018fc3a8-3b76-70f5-84a2-22b84df24739`), this is where the
   dataset (and logs) are stored.

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).
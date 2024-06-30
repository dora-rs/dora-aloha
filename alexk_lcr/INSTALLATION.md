# Dora pipeline for teleoperated low-cost arm and episode recording for LeRobot

AlexK Low Cost Robot is a low-cost robotic arm that can be teleoperated using a similar arm. This repository contains
the Dora pipeline to manipulate the arms, the camera, and record/replay episodes with LeRobot.

## Installation

Dataflow-oriented robotic application (Dora) is a framework that makes creation of robotic applications fast and simple.
See [Dora repository](https://github.com/dora-rs/dora).

**Please read the instructions carefully before installing the required software and environment to run the robot.**

You must install Dora before attempting to run the AlexK Low Cost Robot pipeline. Here are the steps to install Dora:

- Install Rust by following the instructions at [Rustup](https://rustup.rs/). (You may need to install Visual Studio C++
  build tools on Windows.)
- Install Dora by running the following command:

```bash
cargo install dora-cli
```

Now you're ready to run Rust dataflow applications! We decided to only make Python dataflow for AlexK Low Cost Robot, so
you may need to setup your Python environment:

- Install Python 3.8 or later by following the instructions at [Python](https://www.python.org/downloads/).
- Clone this repository by running the following command:

```bash
git clone https://github.com/dora-rs/dora-lerobot
```

- Open a bash terminal and navigate to the root of the submodule `alexk_lcr` in the repository.

```bash
cd dora-lerobot/alexk_lcr
```

- Create a virtual environment by running the following command:

```bash
python -m venv venv
```

- Activate the virtual environment by running the following command:

```bash
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell
```

Finally, install the required Python packages by running the following command:

```bash
pip install -r requirements.txt
```

**Note**: You're totally free to use your own Python environment, a Conda environment, or whatever you prefer, you will
have to activate
your custom python environment before running `dora up && dora start [graph].yml`.

In order to record episodes, you need ffmpeg installed on your system. You can download it from
the [official website](https://ffmpeg.org/download.html).

If you're on Windows, you can download the latest build from [here](https://www.gyan.dev/ffmpeg/builds/). You can
extract the zip file and add the `bin` folder to your PATH.
If you're on Linux, you can install ffmpeg using the package manager of your distribution. (
e.g `sudo apt install ffmpeg` on Ubuntu)

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).
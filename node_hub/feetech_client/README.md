## FeetechClient for SCS/STS motors

This node is a client for the Feetech motors. It is based on the Dynamixel SDK and is used to control the motors. It
is a Python node that communicates with the motors via the USB port.

## YAML Configuration

````YAML
nodes:
  - id: feetech_client
    path: client.py # modify this to the relative path from the graph file to the client script
    inputs:
      pull_present_position: dora/timer/millis/10 # pull the present position every 10ms
      pull_present_velocity: dora/timer/millis/10 # pull the present velocity every 10ms
      pull_goal_position: dora/timer/millis/10 # pull the goal position every 10ms

      # goal_position: some goal position from other node
      # goal_current: some goal current from other node
      # goal_velocity: some goal velocity from other node
    outputs:
      - present_position # regarding 'pull_position' input, it will output the position every 10ms
      - present_velocity # regarding 'pull_velocity' input, it will output the velocity every 10ms
    
      - goal_position # regarding 'pull_goal_position' input, it will output the goal position every 10ms

    env:
      PORT: COM9 # e.g. /dev/ttyUSB0 or COM9
      IDS: 1 2 3 4 5 6

      TORQUE: False False False False False True

      INITIAL_GOAL_POSITION: 1024 None None None None -450
      INITIAL_GOAL_CURRENT: None None None None None 40

      # Determines the offsets and inverts by yourself or by using configuration tools
      HOMING_OFFSET: -2048 2048 2048 -2048 5120 2048
      INVERTED: False True True False True True
````

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).
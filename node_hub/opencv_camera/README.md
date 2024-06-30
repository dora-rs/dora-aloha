## Camera Node for OpenCV compatible cameras

Simple Camera node that uses OpenCV to capture images from a camera. The node can be configured to use a specific camera
id, width and height.
It then sends the images to the dataflow.

## YAML Configuration

````YAML
nodes:
  - id: opencv_camera
    path: camera.py # modify this to the relative path from the graph file to the client script
    inputs:
      pull_image: dora/timer/millis/10 # pull the image every 10ms
      # stop: some stop signal
    outputs:
      - image # push the image to the dataflow 

    env:
      CAMERA_ID: 0 # camera id to use, change this to the camera id you want to use (e.g 0, 1, /dev/video0, /dev/video1)
      CAMERA_WIDTH: 640 # camera width
      CAMERA_HEIGHT: 480 # camera height
````

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).
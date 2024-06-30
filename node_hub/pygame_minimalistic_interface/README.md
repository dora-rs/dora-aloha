## Pygame Minimalistic Interface

Simple Interface that uses Pygame to display images and texts. It also manages keyboard events.
This simple interface can only display two images of the same size side by side and a text in the middle bottom of the
screen.

## YAML Configuration

````YAML
nodes:
  - id: pygame_interface
    path: interface.py # modify this to the relative path from the graph file to the client script
    inputs:
      tick: dora/timer/millis/16 # update the interface every 16ms (= 60fps)

      # write_image_left: some image from other node 
      # write_image_right: some image from other node
      # write_text: some text from other node
    outputs:
      - key_pressed
      - key_released
      - stop

    env:
      CAMERA_WIDTH: 640 # camera width
      CAMERA_HEIGHT: 480 # camera height
````

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).
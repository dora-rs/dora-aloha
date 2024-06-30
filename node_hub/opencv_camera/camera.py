"""
LCR webcam: this Dora node reads the webcam feed of CAMERA_ID and propagates in the dataflow.

1. It reads the webcam feed of CAMERA_ID.
2. It sends the webcam feed to the dataflow.
3. If no camera is found at CAMERA_ID, it sends a black image to the dataflow.

This node also shows the webcam feed in a window.
"""
import os
import cv2
import argparse

import numpy as np
import pyarrow as pa

from dora import Node


def main():
    # Handle dynamic nodes, ask for the name of the node in the dataflow
    parser = argparse.ArgumentParser(
        description="Camera Client: This node is used to represent a camera. ")

    parser.add_argument("--name", type=str, required=False, help="The name of the node in the dataflow.",
                        default="opencv_camera")

    args = parser.parse_args()

    if not os.getenv("CAMERA_ID") or not os.getenv("CAMERA_WIDTH") or not os.getenv("CAMERA_HEIGHT"):
        raise ValueError("Please set the CAMERA_ID, CAMERA_WIDTH, and CAMERA_HEIGHT environment variables")

    camera_id = os.getenv("CAMERA_ID")
    camera_width = os.getenv("CAMERA_WIDTH")
    camera_height = os.getenv("CAMERA_HEIGHT")

    node = Node(args.name)

    if camera_id.isnumeric():
        camera_id = int(camera_id)

    video_capture = cv2.VideoCapture(camera_id)
    font = cv2.FONT_HERSHEY_SIMPLEX

    for event in node:
        event_type = event["type"]

        if event_type == "INPUT":
            event_id = event["id"]

            if event_id == "pull_image":
                ret, frame = video_capture.read()

                if not ret:
                    frame = np.zeros((camera_height, camera_width, 3), dtype=np.uint8)
                    cv2.putText(
                        frame,
                        "No Webcam was found at index %s" % camera_id,
                        (int(30), int(30)),
                        font,
                        0.75,
                        (255, 255, 255),
                        2,
                        1,
                    )

                node.send_output(
                    "image",
                    pa.array(frame.ravel()),
                    event["metadata"],
                )

            if event_id == "stop":
                break

        elif event_type == "STOP":
            break
        elif event_type == "ERROR":
            raise ValueError("An error occurred in the dataflow: " + event["error"])

    video_capture.release()


if __name__ == "__main__":
    main()

"""

"""

import time
import os
import cv2
import argparse
import pygame

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

    if not os.getenv("CAMERA_WIDTH") or not os.getenv("CAMERA_HEIGHT"):
        raise ValueError("Please set the CAMERA_ID, CAMERA_WIDTH, and CAMERA_HEIGHT environment variables")

    camera_width = os.getenv("CAMERA_WIDTH")
    camera_height = os.getenv("CAMERA_HEIGHT")

    image_left = pygame.Surface((int(camera_width), int(camera_height)))
    image_right = pygame.Surface((int(camera_width), int(camera_height)))

    pygame.font.init()
    font = pygame.font.SysFont("Comic Sans MS", 30)
    text = font.render("No text to render", True, (255, 255, 255))

    pygame.init()

    screen = pygame.display.set_mode((int(camera_width) * 2, int(camera_height) + text.get_height() * 2))

    pygame.display.set_caption("Pygame minimalistic interface")

    node = Node(args.name)

    for event in node:
        event_type = event["type"]

        if event_type == "INPUT":
            event_id = event["id"]

            if event_id == "tick":
                quit = False

                for pygame_event in pygame.event.get():
                    if pygame_event.type == pygame.QUIT:
                        quit = True
                    if pygame_event.type == pygame.KEYDOWN:
                        key_str = pygame.key.name(pygame_event.key)
                        node.send_output(
                            "key_pressed",
                            pa.array([key_str], type=pa.string()),
                            event["metadata"]
                        )
                    if pygame_event.type == pygame.KEYUP:
                        key_str = pygame.key.name(pygame_event.key)
                        node.send_output(
                            "key_released",
                            pa.array([key_str], type=pa.string()),
                            event["metadata"]
                        )

                screen.fill((0, 0, 0))

                # Draw the left image
                screen.blit(image_left, (0, 0))

                # Draw the right image
                screen.blit(image_right, (int(camera_width), 0))

                # Draw the text bottom center
                screen.blit(text,
                            (int(camera_width) - text.get_width() // 2, int(camera_height) + text.get_height()))

                pygame.display.flip()

                if quit:
                    break

            elif event_id == "write_image_left":
                raw_data = event["value"].to_numpy()
                image_left = pygame.image.frombuffer(raw_data, (int(camera_width), int(camera_height)), "BGR")

            elif event_id == "write_image_right":
                raw_data = event["value"].to_numpy()
                image_right = pygame.image.frombuffer(raw_data, (int(camera_width), int(camera_height)), "BGR")

            elif event_id == "text":
                text = font.render(event["value"], True, (255, 255, 255))

        elif event_type == "STOP":
            break
        elif event_type == "ERROR":
            raise ValueError("An error occurred in the dataflow: " + event["error"])

    node.send_output(
        "stop",
        pa.array([1], type=pa.int64())
    )

    pygame.quit()


if __name__ == "__main__":
    main()

"""
LCR Saver: This Dora node saves an list of images to a file using ffmpeg.

1. It listens to the dataflow for an image.
2. It saves the image to a file.
3. It listens to the dataflow for a record_episode event.
4. It saves all the images to a video file using ffmpeg.
"""
import os
import cv2
import ffmpeg

import pyarrow as pa

from pathlib import Path

from dora import Node


def main():
    if not os.getenv("RECORD_NAME") or not os.getenv("RECORD_WIDTH") or not os.getenv("RECORD_HEIGHT"):
        raise ValueError("Please set the RECORD_NAME, RECORD_WIDTH, and RECORD_HEIGHT environment variables")

    record_name = os.getenv("RECORD_NAME")

    if not os.getenv("RECORD_WIDTH").isnumeric() or not os.getenv("RECORD_HEIGHT").isnumeric():
        raise ValueError("Please set the RECORD_WIDTH and RECORD_HEIGHT environment variables to integers")

    record_width = int(os.getenv("RECORD_WIDTH"))
    record_height = int(os.getenv("RECORD_HEIGHT"))

    node = Node()
    dataflow_id = node.dataflow_id()

    frames_out_dir = Path("out") / dataflow_id / "frames"
    frames_out_dir.mkdir(parents=True, exist_ok=True)

    episodes_out_dir = Path("out") / dataflow_id / "episodes"
    episodes_out_dir.mkdir(parents=True, exist_ok=True)

    frame_index = 0

    recording_episode = -1

    for event in node:
        event_type = event["type"]

        if event_type == "INPUT":
            event_id = event["id"]

            if event_id == "record" and recording_episode != -1:
                image_dir = frames_out_dir / f"frame_{frame_index:06d}.png"
                frame_index += 1
                image = event["value"].to_numpy().reshape((record_height, record_width, 3))

                cv2.imwrite(str(image_dir), image)

                video_dir = episodes_out_dir / f"{record_name}_{recording_episode}.mp4"
                node.send_output(
                    "saved_image",
                    pa.array([{"path": f"{str(video_dir)}", "timestamp": frame_index / 30}]),
                    event["metadata"],
                )

            elif event_id == "space":
                print(f"Recording episode {recording_episode}", flush=True)
                current_episode = recording_episode
                recording_episode = event["value"].to_numpy()[0]

                if recording_episode == -1:
                    video_dir = episodes_out_dir / f"{record_name}_{current_episode}.mp4"
                    (
                        ffmpeg
                        .input(str(frames_out_dir / 'frame_%06d.png'), format='image2', framerate=30)
                        .output(str(video_dir), vcodec='libx264', g=2, pix_fmt='yuv444p')
                        .global_args('-loglevel', 'error')
                        .run(overwrite_output=True)
                    )
                    frame_index = 0

            elif event_id == "close":
                break

        elif event_type == "STOP":
            break
        elif event_type == "ERROR":
            print("[lcr_record] error: ", event["error"])
            break


if __name__ == "__main__":
    main()

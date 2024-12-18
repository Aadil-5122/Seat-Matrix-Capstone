from ultralytics import YOLO
# from ultralytics.solutions import object_counter
from ultralytics import solutions
import cv2
import time

import logging

from ddb_utils import put_dynamodb_item

logger = logging.getLogger("app_logger")

model = YOLO("yolov8n.pt")
output_path = "results/object_counting_output-4.mp4"

def count_students(path):
    cap = cv2.VideoCapture(path)
    count = {}
    old_counts = {
        "in": -1,
        "out": -1,
    }
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    region_points = [(800, 1335), (1617, 1418), (1698, 1149), (910, 1206)]

    video_writer = cv2.VideoWriter("student_counting.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    region = solutions.ObjectCounter(
        show = False,
        region=region_points,
        model="yolov8n.pt",
        classes=[0],
        show_in=True,
        show_out=True,
    )

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break
        im0 = region.count(im0)
        video_writer.write(im0)
        count = {
            "in": region.in_count,
            "out": region.out_count,
            "timestamp": str(time.time()),
        }

        if count.get('in') != old_counts.get('in') or count.get("out") != old_counts.get("out"):
            old_counts['in'] = count.get('in')
            old_counts['out'] = count.get('out')

            put_dynamodb_item("in_out", count)

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

    return count
from ultralytics import YOLO
# from ultralytics.solutions import object_counter
from ultralytics import solutions
import cv2
import time

import logging

logger = logging.getLogger("app_logger")

model = YOLO("yolo11n.pt")
output_path = "results/object_counting_output-4.mp4"

def count_students(path):
    cap = cv2.VideoCapture(path)
    # cap = cv2.VideoCapture("/home/pratham/happy/Capstone/data/maingate-tester-4.mp4")
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    region_points = [(800, 1335), (1617, 1418), (1698, 1149), (910, 1206)]

    video_writer = cv2.VideoWriter("region_counting.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    region = solutions.ObjectCounter(
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
        print(f"in: {region.in_count} out: {region.out_count}")
        video_writer.write(im0)

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()
    count = {
        "in": region.in_count,
        "out": region.out_count,
        "timestamp": str(time.time()),
    }

    print(count)

    return count
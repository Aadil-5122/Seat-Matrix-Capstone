from ultralytics import YOLO
# from ultralytics.solutions import object_counter
from ultralytics.solutions import object_counter
import cv2

import logging

logger = logging.getLogger("app_logger")

model = YOLO("model/yolov8n.pt")
output_path = "results/object_counting_output-4.mp4"

def count_students(path):
    cap = cv2.VideoCapture(path)
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    line_points = [(800,1335),(1617,1418),(1698,1149),(910,1206)]

    video_writer = cv2.VideoWriter(output_path,
                           cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    counter = object_counter.ObjectCounter()
    counter.set_args(view_img=False,
                     reg_pts=line_points,
                     classes_names=model.names,
                     draw_tracks=True,
                     line_dist_thresh = 5)

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            logger.info("Video frame is empty or video processing has been successfully completed.")
            break
        tracks = model.track(im0, persist=True, show=False, classes= [0],
                            #  tracker='deepsort.yaml'
                             )
        im0 = counter.start_counting(im0, tracks)
        video_writer.write(im0)

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()
    count = {
        "in": counter.in_count,
        "out": counter.out_count,
        "timestamp": counter.timestamp,
    }

    return count
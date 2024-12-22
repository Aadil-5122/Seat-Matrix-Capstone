import cv2
import numpy as np
import json
import copy
from PIL import Image
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('best.pt')

# Scaling factors
scale_x = 2560 / 640  # Width scaling factor
scale_y = 1920 / 640  # Height scaling factor

def iou(box1, box2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.
    box1, box2: [x, y, width, height]
    """
    x1 = max(box1[0], box2[0] - box2[2] / 2)
    y1 = max(box1[1], box2[1] - box2[3] / 2)
    x2 = min(box1[2], box2[0] + box2[2] / 2)
    y2 = min(box1[3], box2[1] + box2[3] / 2)

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = box2[2] * box2[3]

    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0

def map_predictions_to_seats(seat_data, predictions, iou_threshold=0.1):
    """
    Map predictions to saved seat coordinates.
    Assign status based on prediction class: 0 = empty, 1 or 2 = occupied.
    """
    total_occupied = 0
    for seat in seat_data:
        seat["status"] = "empty"

    for pred in predictions:
        pred_box = [pred[0], pred[1], pred[2], pred[3]]
        pred_class = pred[4]  # Class of the prediction
        best_match = None
        best_iou = 0

        for seat in seat_data:
            seat_box = [float(seat["x"]), float(seat["y"]), float(seat["width"]), float(seat["height"])]
            current_iou = iou(pred_box, seat_box)

            if current_iou > best_iou and current_iou >= iou_threshold:
                best_match = seat
                best_iou = current_iou

        if best_match:
            if pred_class == 1 or pred_class == 2:  # Occupied
                best_match["status"] = "occupied"
                total_occupied += 1
            elif pred_class == 0:  # Empty
                best_match["status"] = "empty"

    return seat_data, total_occupied

def seat_status():
    # Load seat coordinates from JSON
    with open(f'./cordinates3.json', 'r') as file:
        seat_data = json.load(file)["boxes"]

    with open("./level4.json", 'r') as file:
        level_data = json.load(file)
    # Video input
    video_path = f'./vlc-record-2024-08-23-22h31m37s-4th floor.mp4-.mp4'
    # video_path = f'./4th floor.mp4'

    output_path = 'output_final.mp4'
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Exit if video ends

        frame_count += 1

        # Run inference on every 60th frame
        if frame_count % 1 == 0:
            # Resize frame to YOLO input size
            resized_frame = cv2.resize(frame, (640, 640))
            results = model(resized_frame, iou=0.6)

            # Parse predictions
            predicted_boxes = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    class_id = int(box.cls[0])  # Class of the prediction
                    predicted_boxes.append([x1, y1, x2, y2, class_id])

            # Map predictions to seats
            updated_seats, total_occupancy = map_predictions_to_seats(seat_data, predicted_boxes)
            updated_seats_copy = copy.deepcopy(updated_seats)
            for seat in updated_seats_copy:
                seat.pop("x")
                seat.pop("y")
                seat.pop("width")
                seat.pop("height")
            # Save updated JSON with statuses
            with open('./seats4.json', 'w') as file:
                json.dump(updated_seats_copy + level_data, file, indent=4)

            with open('./total_occupancy.json', 'w') as file:
                json.dump(total_occupancy, file)
            # print(updated_seats_copy, total_occupancy)

            # Draw bounding boxes for visualization
            for box in predicted_boxes:
                x1, y1, x2, y2, class_id = box
                x1 = int(x1 * scale_x)
                y1 = int(y1 * scale_y)
                x2 = int(x2 * scale_x)
                y2 = int(y2 * scale_y)
                color = (0, 255, 0) if class_id == 0 else (0, 0, 255)  # Green for empty, red for occupied
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # for seat in updated_seats:
            #     if seat["status"] == "occupied":
            #         x, y, w, h = map(int, (
            #             float(seat["x"]) * scale_x,
            #             float(seat["y"]) * scale_y,
            #             float(seat["width"]) * scale_x,
            #             float(seat["height"]) * scale_y
            #         ))
            #         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red box for occupied seats
        
        out.write(frame)
        
        # Display the frame
        cv2.imshow('Video Inference', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Video processing completed.")

if __name__ == '__main__':
    seat_status()

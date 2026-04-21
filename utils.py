from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

def detect_faces_yolo(img):
    results = model(img)

    faces = []
    for r in results:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            faces.append((x1, y1, x2-x1, y2-y1))

    return faces
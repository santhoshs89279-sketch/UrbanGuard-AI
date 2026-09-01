print("Script started")

from ultralytics import YOLO
import requests
from collections import Counter

MODEL_PATH = r"C:\Users\santh\OneDrive\Desktop\Urbangaurd project\UrbanGuard-AI\runs\detect\models\vehicle_detection\yolo11_vehicle\weights\best.pt"

IMAGE_PATH = r"car_test.jpg"

API_URL = "http://localhost:8080/api/vehicles"

print("Loading model...")
model = YOLO(MODEL_PATH)
print("Model loaded successfully")

print("Running detection...")
results = model(IMAGE_PATH)

vehicle_counts = Counter()

for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        vehicle_type = model.names[class_id]

        vehicle_counts[vehicle_type] += 1

        print(f"Detected: {vehicle_type} | Confidence: {confidence:.2%}")

        data = {
            "vehicleType": vehicle_type,
            "confidence": confidence,
            "location": "Camera 1",
            "vehicleCount": 1
        }

        response = requests.post(API_URL, json=data)
        print("Backend response:", response.status_code)

print("\nVehicle Summary:")
for vehicle, count in vehicle_counts.items():
    print(f"{vehicle}: {count}")
from ultralytics import YOLO

# Load your trained model
model = YOLO(
    r"C:\Users\santh\OneDrive\Desktop\Urbangaurd project\UrbanGuard-AI\runs\detect\models\vehicle_detection\yolo11_vehicle\weights\best.pt"
)

# Change this path to an image you want to test
image_path = r"test_image.jpg"

# Run prediction
results = model(image_path)

# Print detected vehicles
for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        vehicle_type = model.names[class_id]

        print(
            f"Vehicle: {vehicle_type} | "
            f"Confidence: {confidence:.2%}"
        )

# Save/display detection result
results[0].show()
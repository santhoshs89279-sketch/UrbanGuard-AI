
from ultralytics import YOLO

def main():
    # Load a small YOLO model
    model = YOLO("yolo11n.pt")

    # Train the model using your processed dataset
    results = model.train(
        data="config/vehicle_data.yaml",
        epochs=10,
        imgsz=416,
        batch=8,
        workers=2,
        patience=3,
        cache=False,
        project="runs/detect",
        name="vehicle_fast"
    )

    print("Training completed!")
    print(results)

if __name__ == "__main__":
    main()

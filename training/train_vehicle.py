from ultralytics import YOLO


# ============================================================
# URBANGUARD AI - VEHICLE DETECTION MODEL TRAINING
# ============================================================

def main():

    print("=" * 60)
    print("URBANGUARD AI - YOLO VEHICLE MODEL TRAINING")
    print("=" * 60)

    # Load lightweight YOLO model
    model = YOLO("yolo11n.pt")

    # Train the model
    results = model.train(
        data="config/vehicle_data.yaml",

        epochs=50,
        imgsz=640,

        batch=4,

        device="cpu",

        workers=0,

        project="models/vehicle_detection",
        name="yolo11_vehicle",

        patience=15,

        pretrained=True,

        verbose=True
    )

    print("\n" + "=" * 60)
    print("TRAINING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
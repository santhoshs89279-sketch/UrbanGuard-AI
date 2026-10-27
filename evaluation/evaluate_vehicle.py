
from pathlib import Path
from ultralytics import YOLO

def main():
    model_path = Path(
        "runs/detect/runs/detect/vehicle_fast/weights/best.pt"
    )
    data_path = Path("config/vehicle_data.yaml")

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset config not found: {data_path}")

    print("=" * 55)
    print("URBANGUARD AI - VEHICLE MODEL EVALUATION")
    print("=" * 55)

    model = YOLO(str(model_path))

    metrics = model.val(
        data=str(data_path),
        split="test",
        imgsz=416,
        batch=8,
        workers=2,
        plots=True,
        project="runs/evaluation",
        name="vehicle_test_eval"
    )

    print("\nTEST DATASET RESULTS")
    print("-" * 40)
    print(f"Precision:  {metrics.box.mp:.4f}")
    print(f"Recall:     {metrics.box.mr:.4f}")
    print(f"mAP50:      {metrics.box.map50:.4f}")
    print(f"mAP50-95:   {metrics.box.map:.4f}")

    print("\nEvaluation completed.")
    print("Results saved in runs/evaluation/vehicle_test_eval")

if __name__ == "__main__":
    main()

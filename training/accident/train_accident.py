
from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = ROOT / "config" / "accident_data.yaml"
MODEL_PATH = ROOT / "runs" / "detect" / "accident_fast" / "weights" / "best.pt"

if not DATA_YAML.exists():
    raise FileNotFoundError(f"Dataset config not found: {DATA_YAML}")

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Trained model not found: {MODEL_PATH}")

print("Starting improved accident detection training...")
print(f"Dataset: {DATA_YAML}")
print(f"Starting weights: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))

model.train(
    data=str(DATA_YAML),
    epochs=30,
    imgsz=416,
    batch=4,
    workers=2,
    device="cpu",
    patience=8,
    project=str(ROOT / "runs" / "detect"),
    name="accident_improved",
    exist_ok=True
)

print("Training finished.")
print("Check the weights at:")
print(ROOT / "runs" / "detect" / "accident_improved" / "weights" / "best.pt")

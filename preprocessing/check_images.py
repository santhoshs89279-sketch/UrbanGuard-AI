from pathlib import Path
from PIL import Image

# Main vehicle dataset folder
DATASET_PATH = Path("data/raw/vehicle")

# Only check these YOLO dataset folders
DATASET_FOLDERS = ["train", "test", "val"]

# Supported image formats
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

total_images = 0
valid_images = 0
missing_labels = []
corrupted_images = []

print("=" * 65)
print("URBANGUARD AI - YOLO VEHICLE DATASET VALIDATION")
print("=" * 65)


for folder_name in DATASET_FOLDERS:

    folder_path = DATASET_PATH / folder_name

    if not folder_path.exists():
        print(f"\nWARNING: Folder not found: {folder_path}")
        continue

    print(f"\nChecking: {folder_path}")

    for image_path in folder_path.rglob("*"):

        if (
            image_path.is_file()
            and image_path.suffix.lower() in IMAGE_EXTENSIONS
        ):

            total_images += 1

            # Check image validity
            try:
                with Image.open(image_path) as img:
                    img.verify()

                valid_images += 1

            except Exception:
                corrupted_images.append(str(image_path))
                continue

            # Check corresponding YOLO label
            label_path = image_path.with_suffix(".txt")

            if not label_path.exists():
                missing_labels.append(str(image_path))


print("\n" + "=" * 65)
print("RESULTS")
print("=" * 65)

print(f"\nTotal YOLO images found : {total_images}")
print(f"Valid images            : {valid_images}")
print(f"Corrupted images        : {len(corrupted_images)}")
print(f"Images without labels   : {len(missing_labels)}")


if corrupted_images:

    print("\nCORRUPTED IMAGES:")

    for image in corrupted_images[:20]:
        print(f"  {image}")


if missing_labels:

    print("\nIMAGES WITHOUT LABELS:")

    for image in missing_labels[:20]:
        print(f"  {image}")


print("\n" + "=" * 65)
print("YOLO DATASET VALIDATION COMPLETED")
print("=" * 65)
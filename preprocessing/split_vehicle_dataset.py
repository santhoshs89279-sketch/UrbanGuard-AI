import shutil
import random
from pathlib import Path


# ============================================================
# URBANGUARD AI - VEHICLE DATASET SPLITTING
# ============================================================

# Original dataset location
SOURCE_DIR = Path(
    "data/raw/vehicle/vehicle/training_image"
)

# Processed dataset location
OUTPUT_DIR = Path(
    "data/processed/vehicle"
)

# Dataset split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

# Reproducible random split
RANDOM_SEED = 42


# ============================================================
# CREATE OUTPUT FOLDERS
# ============================================================

splits = ["train", "val", "test"]

for split in splits:
    (OUTPUT_DIR / split / "images").mkdir(
        parents=True,
        exist_ok=True
    )

    (OUTPUT_DIR / split / "labels").mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# FIND ALL IMAGE FILES
# ============================================================

image_extensions = {".jpg", ".jpeg", ".png"}

images = [
    file
    for file in SOURCE_DIR.iterdir()
    if file.is_file()
    and file.suffix.lower() in image_extensions
]

print("=" * 60)
print("URBANGUARD AI - VEHICLE DATASET SPLITTING")
print("=" * 60)

print(f"\nSource directory: {SOURCE_DIR}")
print(f"Total images found: {len(images)}")


# ============================================================
# SHUFFLE DATASET
# ============================================================

random.seed(RANDOM_SEED)

images.sort()
random.shuffle(images)


# ============================================================
# CALCULATE SPLITS
# ============================================================

total_images = len(images)

train_end = int(total_images * TRAIN_RATIO)
val_end = train_end + int(total_images * VAL_RATIO)

train_images = images[:train_end]
val_images = images[train_end:val_end]
test_images = images[val_end:]


print("\nDataset split:")
print(f"Train: {len(train_images)}")
print(f"Validation: {len(val_images)}")
print(f"Test: {len(test_images)}")


# ============================================================
# VALIDATE YOLO LABEL
# ============================================================

def is_valid_yolo_label(label_path):

    # Empty label files are allowed.
    # They can represent images with no detected object.
    if label_path.stat().st_size == 0:
        return True

    try:
        lines = label_path.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        for line in lines:

            parts = line.split()

            # YOLO detection format:
            # class_id x_center y_center width height
            if len(parts) != 5:
                return False

            class_id = int(parts[0])

            if class_id not in [0, 1, 2, 3]:
                return False

            coordinates = [
                float(value)
                for value in parts[1:]
            ]

            # YOLO coordinates should normally be
            # between 0 and 1
            for value in coordinates:
                if value < 0 or value > 1:
                    return False

        return True

    except Exception:
        return False


# ============================================================
# COPY IMAGES AND LABELS
# ============================================================

def copy_dataset(image_list, split_name):

    copied_images = 0
    copied_labels = 0
    invalid_labels = 0
    missing_labels = 0

    print(f"\nProcessing {split_name.upper()} dataset...")

    for image_path in image_list:

        # Matching label file
        label_path = SOURCE_DIR / (
            image_path.stem + ".txt"
        )

        # Destination paths
        destination_image = (
            OUTPUT_DIR
            / split_name
            / "images"
            / image_path.name
        )

        destination_label = (
            OUTPUT_DIR
            / split_name
            / "labels"
            / label_path.name
        )

        # Copy image
        shutil.copy2(
            image_path,
            destination_image
        )

        copied_images += 1

        # Copy matching label if it exists
        if label_path.exists():

            if is_valid_yolo_label(label_path):

                shutil.copy2(
                    label_path,
                    destination_label
                )

                copied_labels += 1

            else:

                invalid_labels += 1

                print(
                    f"WARNING: Invalid label skipped: "
                    f"{label_path.name}"
                )

        else:

            missing_labels += 1

            print(
                f"WARNING: Missing label: "
                f"{label_path.name}"
            )

    print(f"Images copied: {copied_images}")
    print(f"Labels copied: {copied_labels}")
    print(f"Missing labels: {missing_labels}")
    print(f"Invalid labels: {invalid_labels}")


# ============================================================
# PROCESS ALL SPLITS
# ============================================================

copy_dataset(train_images, "train")

copy_dataset(val_images, "val")

copy_dataset(test_images, "test")


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n" + "=" * 60)
print("DATASET SPLITTING COMPLETED")
print("=" * 60)

print("\nFinal dataset location:")
print(OUTPUT_DIR)

print("\nClasses:")
print("0 = Ambulance")
print("1 = Bus")
print("2 = Car")
print("3 = Truck")

print("\nOriginal dataset was NOT modified.")
print("=" * 60)
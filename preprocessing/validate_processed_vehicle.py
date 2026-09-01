from pathlib import Path
from PIL import Image


# ============================================================
# URBANGUARD AI - PROCESSED YOLO DATASET VALIDATION
# ============================================================

DATASET_DIR = Path("data/processed/vehicle")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

CLASS_NAMES = {
    0: "Ambulance",
    1: "Bus",
    2: "Car",
    3: "Truck"
}


def validate_label(label_path):
    """
    Validate YOLO annotation file.
    Expected format:
    class_id x_center y_center width height
    """

    errors = []
    object_count = 0

    try:

        # Empty labels are allowed
        if label_path.stat().st_size == 0:
            return True, 0, errors

        lines = label_path.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        for line_number, line in enumerate(lines, start=1):

            parts = line.split()

            if len(parts) != 5:
                errors.append(
                    f"{label_path.name} line {line_number}: "
                    f"Expected 5 values, found {len(parts)}"
                )
                continue

            try:
                class_id = int(parts[0])

                if class_id not in CLASS_NAMES:
                    errors.append(
                        f"{label_path.name} line {line_number}: "
                        f"Invalid class ID {class_id}"
                    )
                    continue

                coordinates = [
                    float(value)
                    for value in parts[1:]
                ]

                for value in coordinates:
                    if not 0 <= value <= 1:
                        errors.append(
                            f"{label_path.name} line {line_number}: "
                            f"Coordinate out of range: {value}"
                        )

                object_count += 1

            except ValueError:
                errors.append(
                    f"{label_path.name} line {line_number}: "
                    f"Invalid numeric value"
                )

        return len(errors) == 0, object_count, errors

    except Exception as e:

        errors.append(
            f"{label_path.name}: {str(e)}"
        )

        return False, object_count, errors


def validate_split(split_name):

    image_dir = DATASET_DIR / split_name / "images"
    label_dir = DATASET_DIR / split_name / "labels"

    images = [
        f for f in image_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    labels = list(label_dir.glob("*.txt"))

    corrupted_images = []
    missing_labels = []
    invalid_labels = []
    total_objects = 0

    print("\n" + "=" * 60)
    print(f"VALIDATING: {split_name.upper()}")
    print("=" * 60)

    for image_path in images:

        # ----------------------------------------------------
        # Check image integrity
        # ----------------------------------------------------

        try:

            with Image.open(image_path) as img:
                img.verify()

        except Exception:

            corrupted_images.append(
                image_path.name
            )

            continue

        # ----------------------------------------------------
        # Check matching label
        # ----------------------------------------------------

        label_path = (
            label_dir /
            f"{image_path.stem}.txt"
        )

        if not label_path.exists():

            missing_labels.append(
                image_path.name
            )

            continue

        # ----------------------------------------------------
        # Validate label
        # ----------------------------------------------------

        valid, objects, errors = validate_label(
            label_path
        )

        total_objects += objects

        if not valid:
            invalid_labels.extend(errors)

    # --------------------------------------------------------
    # Find orphan labels
    # --------------------------------------------------------

    orphan_labels = []

    image_stems = {
        image.stem
        for image in images
    }

    for label in labels:

        if label.stem not in image_stems:
            orphan_labels.append(label.name)

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print(f"\nImages found        : {len(images)}")
    print(f"Labels found        : {len(labels)}")
    print(f"Objects found       : {total_objects}")
    print(f"Corrupted images    : {len(corrupted_images)}")
    print(f"Missing labels      : {len(missing_labels)}")
    print(f"Invalid labels      : {len(invalid_labels)}")
    print(f"Orphan labels       : {len(orphan_labels)}")

    return {
        "images": len(images),
        "labels": len(labels),
        "objects": total_objects,
        "corrupted": corrupted_images,
        "missing": missing_labels,
        "invalid": invalid_labels,
        "orphan": orphan_labels
    }


# ============================================================
# MAIN
# ============================================================

print("=" * 60)
print("URBANGUARD AI - FINAL YOLO DATASET VALIDATION")
print("=" * 60)

results = {}

for split in ["train", "val", "test"]:
    results[split] = validate_split(split)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

total_images = sum(
    results[split]["images"]
    for split in results
)

total_labels = sum(
    results[split]["labels"]
    for split in results
)

total_objects = sum(
    results[split]["objects"]
    for split in results
)

total_errors = sum(
    len(results[split]["corrupted"])
    + len(results[split]["missing"])
    + len(results[split]["invalid"])
    + len(results[split]["orphan"])
    for split in results
)

print(f"\nTotal images  : {total_images}")
print(f"Total labels  : {total_labels}")
print(f"Total objects : {total_objects}")
print(f"Total errors  : {total_errors}")

if total_errors == 0:

    print("\nDATASET VALIDATION SUCCESSFUL!")

else:

    print(
        "\nWARNING: DATASET VALIDATION FOUND ERRORS!"
    )

print("=" * 60)
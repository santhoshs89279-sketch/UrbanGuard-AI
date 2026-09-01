import os
import pandas as pd


# ============================================================
# UrbanGuard AI - Dataset Inspection
# ============================================================

DATASET_PATH = os.path.join(
    "data",
    "raw",
    "vehicle"
)


def count_images(folder_path):

    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp"
    )

    count = 0

    for root, dirs, files in os.walk(folder_path):

        for file in files:

            if file.lower().endswith(image_extensions):

                count += 1

    return count


def inspect_dataset():

    print("=" * 60)
    print("URBANGUARD AI - DATASET INSPECTION")
    print("=" * 60)

    # --------------------------------------------------------
    # Check dataset folder
    # --------------------------------------------------------

    if not os.path.exists(DATASET_PATH):

        print("\nERROR: Dataset folder not found.")

        print("Expected location:")

        print(DATASET_PATH)

        return

    print("\nDataset location:")
    print(DATASET_PATH)

    # --------------------------------------------------------
    # List files and folders
    # --------------------------------------------------------

    print("\nDataset contents:")

    for item in os.listdir(DATASET_PATH):

        item_path = os.path.join(
            DATASET_PATH,
            item
        )

        if os.path.isdir(item_path):

            print(f"  [FOLDER] {item}")

        else:

            print(f"  [FILE]   {item}")

    # --------------------------------------------------------
    # Count images
    # --------------------------------------------------------

    image_data_path = os.path.join(
        DATASET_PATH,
        "image_data"
    )

    training_image_path = os.path.join(
        DATASET_PATH,
        "training_image"
    )

    if os.path.exists(image_data_path):

        count = count_images(
            image_data_path
        )

        print("\nImages in image_data:")
        print(count)

    if os.path.exists(training_image_path):

        count = count_images(
            training_image_path
        )

        print("\nImages in training_image:")
        print(count)

    # --------------------------------------------------------
    # Read image metadata
    # --------------------------------------------------------

    metadata_file = os.path.join(
        DATASET_PATH,
        "image_metadata.csv"
    )

    if os.path.exists(metadata_file):

        print("\n" + "-" * 60)
        print("IMAGE METADATA")
        print("-" * 60)

        metadata = pd.read_csv(
            metadata_file
        )

        print("\nRows:")
        print(len(metadata))

        print("\nColumns:")

        for column in metadata.columns:

            print(f"  - {column}")

        print("\nFirst 5 rows:")

        print(
            metadata.head()
        )

    else:

        print(
            "\nimage_metadata.csv not found."
        )

    # --------------------------------------------------------
    # Read sensor data
    # --------------------------------------------------------

    sensor_file = os.path.join(
        DATASET_PATH,
        "sensor_data.csv"
    )

    if os.path.exists(sensor_file):

        print("\n" + "-" * 60)
        print("SENSOR DATA")
        print("-" * 60)

        sensor = pd.read_csv(
            sensor_file
        )

        print("\nRows:")
        print(len(sensor))

        print("\nColumns:")

        for column in sensor.columns:

            print(f"  - {column}")

        print("\nFirst 5 rows:")

        print(
            sensor.head()
        )

    else:

        print(
            "\nsensor_data.csv not found."
        )

    print("\n" + "=" * 60)
    print("DATASET INSPECTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":

    inspect_dataset()
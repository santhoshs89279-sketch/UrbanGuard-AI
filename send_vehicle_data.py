import requests

API_URL = "http://localhost:8080/api/vehicles"

def send_vehicle_detection(vehicle_type, confidence, location, vehicle_count):
    data = {
        "vehicleType": vehicle_type,
        "confidence": confidence,
        "location": location,
        "vehicleCount": vehicle_count
    }

    try:
        response = requests.post(API_URL, json=data)

        if response.status_code == 200:
            print("Vehicle data sent successfully!")
            print(response.json())
        else:
            print("Failed to send data:", response.status_code)
            print(response.text)

    except Exception as e:
        print("Error:", e)


send_vehicle_detection(
    "Car",
    0.95,
    "Main Road Junction",
    1
)
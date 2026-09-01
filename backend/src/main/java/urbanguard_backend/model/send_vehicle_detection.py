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
            print("Vehicle detection sent successfully!")
            print(response.json())
        else:
            print("Failed to send detection:", response.status_code)
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("Could not connect to the backend. Make sure Spring Boot is running.")


# Test the connection
if __name__ == "__main__":
    send_vehicle_detection(
        vehicle_type="Car",
        confidence=0.95,
        location="UrbanGuard Camera 1",
        vehicle_count=1
    )
import requests
import tests.test_users_infos as test_users_infos

# URL der API
BASE_URL = "http://127.0.0.1:5000"

# Beispielbenutzerdaten
USERNAME = ""  # Replace with your username
PASSWORD = test_users_infos.password  # Replace with your password
SECRET = None
USER_ID = None


def login():
    """
    Logs in the test user using POST /login route.
    """
    global SECRET, USER_ID
    print("Testing login...")

    response = requests.post(f"{BASE_URL}/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })

    if response.status_code == 200:
        response_data = response.json()
        SECRET = response_data.get("secret")
        USER_ID = response_data.get("user_id")
        print(f"Login successful! User ID: {USER_ID}, Secret: {SECRET}")
    else:
        print(f"Login failed! Error: {response.json()}")
    return response.status_code


def change_data():
    """
    Updates user-specific data via PUT /data route.
    """
    print("Testing data changes...")
    if not SECRET or not USER_ID:
        print("Error: Missing SECRET or USER_ID (Please log in first).")
        return

    # Payload for updating user data
    response = requests.put(f"{BASE_URL}/data", json={
        "user_id": USER_ID,
        "secret": SECRET,
        "data": {
            "level": 65
        }
    })

    if response.status_code == 200:
        print(f"Data updated successfully: {response.json()}")
    else:
        print(f"Failed to update data! Error: {response.json()}")
    return response.status_code


if __name__ == "__main__":
    # Run Test
    if login() == 200:
        change_data()
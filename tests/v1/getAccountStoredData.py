import requests
import tests.test_users_infos as test_users_infos

# API URL
BASE_URL = "http://127.0.0.1:5000"

# Beispielbenutzerdaten
USERNAME = ""  # Replace with your test username
PASSWORD = test_users_infos.password  # Replace with your test password
SECRET = None
USER_ID = None


def login():
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


def get_user_data():
    """
    Retrieve user account data using the GET /account route with secret authentication.
    """
    print("Testing user data retrieval...")
    if not SECRET or not USER_ID:
        print("Error: Missing SECRET or USER_ID (Please log in first).")
        return

    # Using the `/account` route for retrieval
    response = requests.get(f"{BASE_URL}/account", params={"user_id": USER_ID, "secret": SECRET})

    if response.status_code == 200:
        print("User data retrieved successfully:")
        print(response.json())
    else:
        print(f"Failed to retrieve user data! Error: {response.json()}")
    return response.status_code


if __name__ == "__main__":
    # Run Test
    if login() == 200:
        get_user_data()
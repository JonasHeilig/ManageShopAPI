import requests
import uuid
import tests.test_users_infos as test_users_infos

# URL of the running Flask app
BASE_URL = "http://127.0.0.1:5000"

# Global data for testing
USERNAME = f"test_user_{uuid.uuid4().hex[:6]}"
PASSWORD = test_users_infos.password
USER_ID = None
SECRET = None


def create_account():
    """
    Creates an account using POST /account route.
    """
    url = f"{BASE_URL}/account"
    account_data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(url, json=account_data)
        if response.status_code == 201:
            print("Account created successfully!")
            print("Response:", response.json())
            global USER_ID, SECRET
            USER_ID = response.json().get("user_id")
            SECRET = response.json().get("secret")
        else:
            print(f"Failed to create account. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def login():
    """
    Logs in using POST /login route.
    """
    url = f"{BASE_URL}/login"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(url, json=login_data)
        if response.status_code == 200:
            print("Login successful!")
            print("Response:", response.json())
            global USER_ID, SECRET
            USER_ID = response.json().get("user_id")
            SECRET = response.json().get("secret")
        else:
            print(f"Failed to login. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def update_user_data():
    """
    Updates user data using PUT /data route.
    """
    url = f"{BASE_URL}/data"
    user_data = {
        "user_id": USER_ID,
        "secret": SECRET,
        "data": {
            "level": 10,
            "score": 4500,
            "preferences": {"theme": "dark"}
        }
    }

    try:
        response = requests.put(url, json=user_data)
        if response.status_code == 200:
            print("User data updated successfully!")
            print("Response:", response.json())
        else:
            print(f"Failed to update user data. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def get_account_data():
    """
    Retrieves account data using GET /account route.
    """
    url = f"{BASE_URL}/account"
    params = {
        "user_id": USER_ID,
        "secret": SECRET
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("Account data retrieved successfully!")
            print("Response:", response.json())
            assert response.json().get("username") == USERNAME, "Username does not match expected value."
        else:
            print(f"Failed to retrieve account data. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def get_user_data():
    """
    Retrieves user stored data using GET /data route.
    """
    url = f"{BASE_URL}/data"
    params = {
        "user_id": USER_ID,
        "secret": SECRET
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("User data retrieved successfully!")
            print("Response:", response.json())
        else:
            print(f"Failed to retrieve user data. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def main():
    """
    Executes a sequence of tests for account and user data functionality.
    """
    print("--- Testing Account Creation ---")
    create_account()

    print("\n--- Testing Login ---")
    login()

    print("\n--- Testing User Data Update ---")
    update_user_data()

    print("\n--- Testing Account Data Retrieval ---")
    get_account_data()

    print("\n--- Testing Get User Stored Data ---")
    get_user_data()


if __name__ == "__main__":
    main()

import requests
import uuid

# URL of the running Flask app
BASE_URL = "http://127.0.0.1:5000"

# Global data for testing
USERNAME = f"test_user_{uuid.uuid4().hex[:6]}"
PASSWORD = "securepassword123"
USER_ID = None
SECRET = None


def create_account():
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
        else:
            print(f"Failed to login. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def update_user_data():
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


def add_product():
    url = f"{BASE_URL}/product"
    product_data = {
        "name": "Test2",
        "description": "Test coins for your account",
        "price": 7.99,
        "tax_behavior": "inclusive"
    }

    try:
        response = requests.post(url, json=product_data)
        if response.status_code == 201:
            print("Product created successfully!")
            print("Response:", response.json())
        else:
            print(f"Failed to create product. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def main():
    print("--- Testing Account Creation ---")
    create_account()
    # print("\n--- Account for this test already created ---")

    print("\n--- Testing Login ---")
    login()

    print("\n--- Testing User Data Update ---")
    update_user_data()

    print("\n--- Testing Add Product ---")
    add_product()
    # print("\n--- It Works :) ---")


if __name__ == "__main__":
    main()

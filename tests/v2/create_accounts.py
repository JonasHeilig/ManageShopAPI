import requests
import uuid
import tests.test_users_infos as pwf

# Base URL of the application from app.py
BASE_URL = "http://127.0.0.1:5000"

# Local test_users_infos list to temporarily store created account data
test_users_infos = []


def create_account(username, password):
    """
    Creates an account by sending a POST request to the /account route in app.py.
    """
    url = f"{BASE_URL}/account"  # Endpoint defined in app.py
    account_data = {
        "username": username,
        "password": password
    }

    try:
        # Sending the POST request
        response = requests.post(url, json=account_data)

        # Handling status 201 for successful creation
        if response.status_code == 201:
            print("Account created successfully!")
            try:
                response_json = response.json()
                return {
                    "user_id": response_json.get("user_id"),
                    "secret": response_json.get("secret")
                }
            except ValueError:
                print("Failed to parse JSON response.")
                return None
        else:
            # Handling errors from the API
            print(f"Failed to create account. Status code: {response.status_code}")
            print("Response text:", response.text)
            return None
    except requests.RequestException as e:
        # Handling general network-related errors
        print(f"An error occurred: {e}")
        return None


def bulk_create_accounts():
    """
    Prompts the user for the number of accounts to create, then creates them.
    """
    try:
        # Prompt user for number of accounts to create
        num_accounts = int(input("How many accounts would you like to create? "))
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    if num_accounts <= 0:
        print("The number of accounts must be greater than zero.")
        return

    print(f"Creating {num_accounts} accounts...\n")
    for i in range(num_accounts):
        username = f"test_user_{uuid.uuid4().hex[:6]}"
        password = pwf.password
        print(f"Creating account {i + 1} with username: {username} and password: {password}...")
        account_data = create_account(username, password)
        if account_data:
            test_users_infos.append(account_data)  # Store account data locally

    # Final output
    print("\nAccount creation completed!")
    print(f"Created {len(test_users_infos)} accounts:")
    for index, account in enumerate(test_users_infos):
        print(f"  {index + 1}. User ID: {account['user_id']}, Secret: {account['secret']}")


# Main script entry point
if __name__ == "__main__":
    bulk_create_accounts()
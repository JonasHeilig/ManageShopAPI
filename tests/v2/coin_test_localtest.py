import requests
import sqlite3
import os
import tests.test_users_infos as test_users_infos

# API URL
BASE_URL = "http://127.0.0.1:5000"

# Local database path
DATABASE_PATH = 'Insert Path Here'

# Global variables to store session information
USER_ID = None
SECRET = None
PASSWORD = test_users_infos.password


def print_intro():
    """
    Print introduction text for the tool.
    """
    print("Welcome to the Coin Management Test Script!")
    print("This script allows you to manage coins for test users.")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    input("Press any key to continue...")


def fetch_local_users():
    """
    Fetches all usernames from the local SQLite database.
    """
    if not os.path.exists(DATABASE_PATH):
        print(f"Database not found at {DATABASE_PATH}")
        return []

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Try to fetch usernames from the 'user' table
    try:
        cursor.execute("SELECT username FROM user")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"Error accessing the database: {e}")
        return []
    finally:
        conn.close()


def select_user(usernames):
    """
    Allows the tester to select a username from the list of fetched usernames.
    """
    print("\n--- Available Users ---")
    for index, username in enumerate(usernames, start=1):
        print(f"{index}. {username}")

    while True:
        try:
            selection = int(input("\nSelect a user by entering the corresponding number: "))
            if 1 <= selection <= len(usernames):
                return usernames[selection - 1]
            else:
                print("Invalid selection, please try again.")
        except ValueError:
            print("Please enter a valid number.")


def login_user(username):
    """
    Logs in the selected user and reports back status and errors.
    """
    global USER_ID, SECRET
    url = f"{BASE_URL}/login"
    login_data = {
        "username": username,
        "password": PASSWORD
    }

    print(f"Attempting to log in user '{username}' with password: '{PASSWORD}'...")

    try:
        response = requests.post(url, json=login_data)
        print(f"Login response status code: {response.status_code}")
        print(f"Login response: {response.json()}")  # Full debugging output for the response

        if response.status_code == 200:
            print("Login successful!")
            data = response.json()
            USER_ID = data.get("user_id")
            SECRET = data.get("secret")
            return USER_ID, SECRET
        else:
            print(f"Login failed for user: {username}. Status code: {response.status_code}")
            print("Error details:", response.json())
            return None, None
    except requests.RequestException as e:
        print(f"An unexpected error occurred during login: {e}")
        return None, None


def view_coins(user_id, secret):
    """
    Retrieves and displays the number of coins for a given user using the GET /account route.
    """
    response = requests.get(f"{BASE_URL}/account", params={"user_id": user_id, "secret": secret})
    if response.status_code == 200:
        data = response.json()
        print(f"User's coins: {data['coins']}")
    else:
        print("Failed to fetch coin data!")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")


def update_coins(user_id, secret, action, amount):
    """
    Updates the user's coin balance using the PUT /account route.
    """
    # Validate action to exclude 'set'
    if action not in ["add", "deduct"]:
        print("Invalid action! Only 'add' and 'deduct' are allowed.")
        return

    response = requests.put(f"{BASE_URL}/account", json={
        "user_id": user_id,
        "secret": secret,
        "action": action,  # Can only be "add" or "deduct"
        "amount": amount
    })

    if response.status_code == 200:
        data = response.json()
        print(f"Coins successfully updated. New balance: {data['coins']}")
    else:
        print("Failed to update coins!")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")


def manage_coins(user_id, secret):
    """
    Provides options for the tester to manage user coins:
    View coins, add coins, remove coins, set coins directly, or navigate back.
    """
    while True:
        print("\n--- Coin Management ---")
        print("1. View coins")
        print("2. Remove coins")
        print("3. Add coins")
        print("4. Back to user selection")
        print("5. Exit")

        try:
            choice = int(input("Choose an option (1-6): "))
            if choice == 1:
                view_coins(user_id, secret)
            elif choice == 2:
                amount = int(input("Enter the number of coins to remove: "))
                update_coins(user_id, secret, action="deduct", amount=amount)
            elif choice == 3:
                amount = int(input("Enter the number of coins to add: "))
                update_coins(user_id, secret, action="add", amount=amount)
            elif choice == 4:
                # Return to the user selection
                return "back"
            elif choice == 5:
                # Exit the script
                print("Exiting the script. Goodbye!")
                exit()
            else:
                print("Invalid selection, please try again.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    """
    Main logic for the tool.
    """
    print_intro()

    while True:
        # Fetch usernames from the local SQLite database
        usernames = fetch_local_users()
        if not usernames:
            print("No users found in the database!")
            print("Ensure your database is properly initialized with test users.")
            return

        # Display list of users for selection
        selected_username = select_user(usernames)

        # Log in the selected user
        user_id, secret = login_user(selected_username)
        if not user_id:
            print("Login failed. Returning to user selection...")
            continue

        # Allow the user to manage coins
        result = manage_coins(user_id, secret)

        # If user chooses to go back to user selection, restart the loop
        if result == "back":
            continue


# Entry point for the tool
if __name__ == "__main__":
    main()
import requests

# URL of the running Flask app
BASE_URL = "http://127.0.0.1:5000"


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


if __name__ == "__main__":
    add_product()

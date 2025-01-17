import requests

# URL of the running Flask app
BASE_URL = "http://127.0.0.1:5000"

# Data for the new product
product_data = {
    "name": "Test Product",
    "description": "Test Product",
    "price": 3.99,
    "tax_behavior": "inclusive"
}


def create_product():
    url = f"{BASE_URL}/product"

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
    create_product()

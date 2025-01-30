import requests

# URL der API
BASE_URL = "http://127.0.0.1:5000"

# Beispielbenutzerdaten
USERNAME = "test_user_93f2b9"  # Ersetze dies mit deinem Benutzernamen
PASSWORD = "securepassword123"  # Ersetze dies mit deinem Passwort
SECRET = None
USER_ID = None


def login():
    global SECRET, USER_ID
    print("Teste Login...")

    response = requests.post(f"{BASE_URL}/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })

    if response.status_code == 200:
        response_data = response.json()
        SECRET = response_data.get("secret")
        USER_ID = response_data.get("user_id")
        print(f"Login erfolgreich! Nutzer-ID: {USER_ID}, Secret: {SECRET}")
    else:
        print(f"Login fehlgeschlagen! Fehler: {response.json()}")
    return response.status_code


def get_user_data():
    print("Teste Abrufen der Benutzerdaten...")

    if not SECRET or not USER_ID:
        print("Fehler: Kein SECRET oder USER_ID verfügbar (Bitte zuerst einloggen).")
        return

    response = requests.get(f"{BASE_URL}/data", params={
        "user_id": USER_ID,
        "secret": SECRET
    })

    if response.status_code == 200:
        print("Benutzerdaten erfolgreich abgerufen:")
        print(response.json())
    else:
        print(f"Abrufen der Benutzerdaten fehlgeschlagen! Fehler: {response.json()}")
    return response.status_code


if __name__ == "__main__":
    # Run Test
    if login() == 200:
        get_user_data()
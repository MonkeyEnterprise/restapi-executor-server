import requests
import time
import os

API_URL = "https://parentpager.pouwertronics.nl"
API_KEY = "JOUW-GEHEIME-API-KEY"  # Zorg ervoor dat je de juiste API-key gebruikt
ENDPOINTS = ["/v1/stage/state", "/version"]

def fetch_data(endpoint):
    url = f"{API_URL}{endpoint}"
    headers = {"X-API-KEY": API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {endpoint}: {response.status_code}")
        return None

def main():
    while True:
        for endpoint in ENDPOINTS:
            data = fetch_data(endpoint)
            if data:
                print(f"Data from {endpoint}: {data}")
                # Hier kun je de data verder verwerken of integreren met ProPresenter
        time.sleep(10)  # Wacht 10 seconden voordat je opnieuw ophaalt

if __name__ == "__main__":
    main()

import requests
import time
import os

def register_ip():
    # Verkrijg het IP van de Raspberry Pi, kan dynamisch worden geconfigureerd
    ip = os.environ['PC1_IP']  # Dit haalt het IP van de Flask-container op
    try:
        response = requests.post(f"{ip}/register_ip", json={'ip': ip})
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Fout bij het registreren van IP: {e}")

# Herhaal de registratie elke 5 minuten
while True:
    register_ip()
    time.sleep(300)  # 5 minuten wachten

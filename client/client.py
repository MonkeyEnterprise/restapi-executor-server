import time
import requests

SERVER_URL = "http://server-ip:5000/callsToExecute"
STATUS_UPDATE_URL = "http://server-ip:5000/updateStatus"
PROPRESENTER_URL = "http://localhost:5000"

def fetch_commands():
    try:
        response = requests.get(SERVER_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Server error: {response.status_code}")
    except Exception as e:
        print(f"Error fetching commands: {e}")
    return []

def send_status_update(command, response):
    status_payload = {
        "command": command,
        "status_code": response.status_code,
        "response": response.text
    }
    try:
        requests.post(STATUS_UPDATE_URL, json=status_payload)
    except Exception as e:
        print(f"Failed to send status update: {e}")

def execute_command(command):
    try:
        url = f"{PROPRESENTER_URL}/{command['endpoint']}"
        method = command.get("method", "POST").upper()
        data = command.get("data", {})

        if method == "POST":
            response = requests.post(url, json=data)
        else:
            response = requests.get(url, params=data)

        send_status_update(command, response)
    except Exception as e:
        print(f"Error executing command: {e}")

while True:
    commands = fetch_commands()
    for cmd in commands:
        execute_command(cmd)
    time.sleep(5)

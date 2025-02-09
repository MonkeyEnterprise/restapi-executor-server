import socketio
import requests

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.on('get_version')
def on_get_version(data):
    print("Received version request")
    # Voer het GET-verzoek uit naar het lokale apparaat
    response = requests.get("http://localhost:8000/version")
    sio.emit('version_response', response.json())

sio.connect("http://raspberrypi-ip:5000")
sio.wait()

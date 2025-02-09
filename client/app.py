import socketio
import requests
import uuid

# Initialiseer socketio client
sio = socketio.Client()

# Genereer een client_id voor deze client
client_id = str(uuid.uuid4())
print(f"Client ID: {client_id}")

# Event bij verbinden
@sio.event
def connect():
    print("✅ Verbonden met de server!")

# Event bij het ontvangen van een 'get_version' bericht
@sio.on('get_version')
def on_get_version(data):
    print("🔄 Versieaanvraag ontvangen...")
    
    # Ophalen van de versie bij de API
    try:
        response = requests.get("http://192.168.100.30:8000/version", timeout=5)
        response.raise_for_status()  # Controleer of het een succesvolle response was
        version_data = response.json()

        # Stuur de versie terug naar de server met het request_id en de client_id
        sio.emit('version_response', {
            'request_id': data['request_id'],
            'client_id': client_id,  # Voeg client_id toe aan het antwoord
            'version': version_data
        })
        print("✅ Versie verstuurd!")

    except requests.exceptions.RequestException as e:
        print(f"❌ Fout bij ophalen versie: {e}")
        sio.emit('version_response', {"error": "failed to get version", 'client_id': client_id})

# Verbinding maken met de server, met client_id als parameter
try:
    print(f"Verbindingsheaders: {{'client_id': {client_id}}}")
    sio.connect("http://192.168.100.2:7000", headers={"client_id": client_id}, wait_timeout=5)
except socketio.exceptions.ConnectionError:
    print("❌ Kan geen verbinding maken met de server!")

# Wacht op events
sio.wait()

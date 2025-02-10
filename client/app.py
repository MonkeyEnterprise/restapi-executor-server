import socketio
import requests
import logging

# Initialisatie van de SocketIO client
sio = socketio.Client()
client_id = "client2"  # Dynamisch client_id, moet overeenkomen met wat de server verwacht
server_url = "http://192.168.100.2:5000"  # Serveradres

logging.basicConfig(level=logging.INFO)

@sio.event
def connect():
    """Verbind met de server en registreer."""
    logging.info("Verbonden met de server")
    sio.emit('register', {'client_id': client_id})  # Stuur het client_id naar de server

@sio.on('request_version')
def request_version(data):
    """Verzoek om versie-informatie van de server verwerken en antwoord sturen."""
    request_id = data.get('request_id')  # Verkrijg het request_id
    requester_id = data.get('requester_id')  # Verkrijg het requester_id (client1)
    logging.info(f"Versie-aanvraag ontvangen voor {requester_id}, request_id: {request_id}")

    try:
        # Doe het verzoek naar de versie-api van de client2
        response = requests.get("http://192.168.100.30:8000/version")
        version_data = response.json()  # Verkrijg de versie-informatie
        logging.info(f"Versie-info opgehaald: {version_data}")

        # Stuur het resultaat terug naar de server (en de requester)
        sio.emit('version_info', {
            'request_id': request_id,  # Voeg het request_id toe voor identificatie
            'version_data': version_data
        })
    except Exception as e:
        logging.error(f"Fout bij ophalen versie: {e}")

# Verbind met de server
sio.connect(server_url)
sio.wait()

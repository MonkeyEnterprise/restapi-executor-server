import socketio
from flask import Flask, request, jsonify
import logging
import uuid
from flask_socketio import SocketIO

app = Flask(__name__)

# Maak een SocketIO server
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

clients = {}  # Opslag van client_id -> socket_id
pending_requests = {}  # Opslag van verzoeken {request_id: client_id}

logging.basicConfig(level=logging.INFO)


@app.route('/version', methods=['GET'])
def get_version():
    """Client1 vraagt de versie op, de server stuurt het verzoek naar een beschikbare Client2."""
    client_id = request.headers.get('X-Client-ID')
    logging.info(f"Ontvangen versie-verzoek van {client_id}")

    if not client_id:
        return jsonify({"status": "error", "message": "X-Client-ID header is vereist"}), 400

    # Genereer een uniek request_id en sla het op
    request_id = str(uuid.uuid4())
    pending_requests[request_id] = client_id
    logging.info(f"Versie-verzoek doorgestuurd naar client2 met request_id {request_id}")

    # Stuur een WebSocket-event naar client2
    if 'client2' in clients:
        socketio.emit('request_version', {'requester_id': client_id, 'request_id': request_id}, room=clients['client2'])
    else:
        logging.warning("Geen client2 geregistreerd")

    return jsonify({
        "status": "success",
        "message": f"Versie-aanvraag naar client2 gestuurd",
        "request_id": request_id
    })


@socketio.on('register')
def handle_register(data):
    """Client2 registreert zichzelf bij de server."""
    client_id = data.get('client_id')

    if not client_id:
        logging.warning("Client probeerde te registreren zonder client_id")
        return

    clients[client_id] = request.sid
    logging.info(f"Client {client_id} geregistreerd met socket ID {request.sid}")


@socketio.on('version_info')
def handle_version_info(data):
    """Client2 stuurt de versie-info terug, en de server geeft het door aan Client1."""
    request_id = data.get('request_id')
    version_data = data.get('version_data')

    logging.info(f"Versie-info ontvangen voor request_id {request_id}, terugsturen naar client1")

    # Zoek naar de client die het verzoek heeft gedaan
    if request_id in pending_requests:
        requester_id = pending_requests.pop(request_id)  # Verkrijg de client_id die het verzoek heeft gedaan
        logging.info(f"Versie-info voor request_id {request_id} wordt teruggestuurd naar {requester_id}")

        # Stuur versie-informatie als een enkele response naar client1
        socketio.emit('version_response', {
            'status': 'success',
            'message': 'Versie-informatie ontvangen',
            'request_id': request_id,
            'response': version_data
        }, room=clients[requester_id])

    else:
        logging.warning(f"Geen openstaande verzoeken voor request_id {request_id}, kan geen versie-info terugsturen")


@socketio.on('disconnect')
def handle_disconnect():
    """Verwijder een client als deze de verbinding verbreekt."""
    disconnected_client = None
    for cid, sid in clients.items():
        if sid == request.sid:
            disconnected_client = cid
            break

    if disconnected_client:
        del clients[disconnected_client]
        logging.info(f"Client {disconnected_client} is losgekoppeld")


# Start de server met eventlet
if __name__ == '__main__':
    logging.info("Server wordt gestart op poort 5000...")
    socketio.run(app, host='0.0.0.0', port=5000)

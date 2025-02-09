import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import uuid

# Logging instellen
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}  # Opslag voor verbonden clients {client_id: request.sid}
pending_requests = {}  # Opslag voor lopende versieaanvragen {request_id: client_id}

@app.route('/api/version', methods=['GET'])
def handle_version_request():
    client_id = request.args.get("client_id")
    if client_id in clients:  # Controleer of client_id bestaat in de 'clients' dictionary
        request_id = str(uuid.uuid4())  # Genereer een unieke request-ID
        pending_requests[request_id] = client_id  # Koppel het verzoek aan de client
        logger.info(f"Versieaanvraag ({request_id}) verzonden naar client {client_id}")
        
        socketio.emit('get_version', {'request_id': request_id}, room=clients[client_id])
        return jsonify({"status": "sent", "request_id": request_id}), 200
    
    logger.warning("Client niet verbonden")
    return jsonify({"error": "client not connected"}), 400

@socketio.on('connect')
def handle_connect():
    client_id = request.headers.get("client_id")  # Verkrijg client_id uit headers
    if client_id:
        clients[client_id] = request.sid  # Koppel client_id aan sid
        logger.info(f"Client verbonden: {client_id} (sid: {request.sid})")
    else:
        logger.warning("Geen client_id ontvangen bij connectie.")

@socketio.on('disconnect')
def handle_disconnect():
    client_id = next((key for key, value in clients.items() if value == request.sid), None)
    if client_id:
        clients.pop(client_id)  # Verwijder client uit de 'clients' dictionary
        logger.info(f"Client verbroken: {client_id} (sid: {request.sid})")

@socketio.on('version_response')
def handle_version_response(data):
    request_id = data.get("request_id")
    version = data.get("version")
    client_id = data.get("client_id")  # Ontvang client_id
    
    if request_id in pending_requests:
        # Zoek de client_id in de pending_requests
        original_client_id = pending_requests.pop(request_id)
        
        # Verzend de versieinformatie naar de juiste client (browser)
        if original_client_id == client_id:
            logger.info(f"Versie ontvangen van client {client_id}: {version}")
            # Gebruik de client_id om het antwoord terug te sturen naar de juiste socket
            socketio.emit('version_info', {'version': version}, room=clients[original_client_id])
        else:
            logger.warning(f"Client ID mismatch voor request_id {request_id}. Verwacht {original_client_id}, maar ontvangen {client_id}.")
    else:
        logger.warning(f"Onbekende versie-response ontvangen: {data}")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)

import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit

# Logging instellen
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}

@app.route('/api/version', methods=['GET'])
def handle_version_request():
    client_id = request.args.get("client_id")
    if client_id in clients:
        logger.info(f"Versieaanvraag verzonden naar client {client_id}")
        socketio.emit('get_version', {}, room=clients[client_id])
        return {"status": "sent"}, 200
    logger.warning("Client niet verbonden")
    return {"error": "client not connected"}, 400

@socketio.on('connect')
def handle_connect():
    clients[request.sid] = request.sid
    logger.info(f"Client verbonden: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    clients.pop(request.sid, None)
    logger.info(f"Client verbroken: {request.sid}")

@socketio.on('version_response')
def handle_version_response(data):
    logger.info(f"Versie ontvangen: {data}")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)

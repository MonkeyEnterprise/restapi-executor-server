from flask import Flask, request, jsonify

app = Flask(__name__)

# Initieel IP-adres is None
pc1_ip = None

@app.route('/register_ip', methods=['POST'])
def register_ip():
    global pc1_ip
    pc1_ip = request.json.get('ip')  # Haal het IP-adres op van de Raspberry Pi
    return jsonify({'status': 'success', 'ip': pc1_ip})

@app.route('/version', methods=['GET'])
def version():
    if pc1_ip:
        # Geef versie-informatie terug via het geregistreerde IP van PC 1
        return jsonify({'status': 'success', 'ip': pc1_ip, 'version': '1.0.0'})
    return jsonify({'status': 'failure', 'message': 'IP niet geregistreerd'})

@app.route('/v1/stage/state', methods=['GET'])
def stage_state():
    # Hier kun je de logica toevoegen voor de /v1/stage/state endpoint
    return jsonify({'state': 'active'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

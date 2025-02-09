import requests
from flask import Flask, jsonify

app = Flask(__name__)

PRO_PRESENTER_API_URL = "http://localhost:5000/api"  # Lokale ProPresenter API

@app.route('/v1/stage/state', methods=['GET', 'POST'])
def stage_state():
    try:
        response = requests.get(f"{PRO_PRESENTER_API_URL}/stage/state")
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/version', methods=['GET', 'POST'])
def version():
    try:
        response = requests.get(f"{PRO_PRESENTER_API_URL}/version")
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

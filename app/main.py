##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
##

from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, request, jsonify
import logging
import os
import uuid
import threading
import argparse
from functools import wraps
from typing import Optional, Tuple, Dict, Any, List


class RequestQueue:
    def __init__(self) -> None:
        self.requests: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def add(self, request_data: dict) -> Tuple[dict, int]:
        if not isinstance(request_data, dict):
            logging.error(f"Expected dict, but got {type(request_data).__name__}")
            return {"error": "Invalid request data"}, 400

        try:
            unique_id = str(uuid.uuid4())
            request_data["uuid"] = unique_id

            with self.lock:
                self.requests.append(request_data)

            logging.info("Request queued successfully: %s", request_data)
            return {"status": "queued", "uuid": unique_id}, 200

        except Exception as e:
            logging.exception("Error enqueuing request")
            return {"error": "Internal server error"}, 500

    def get(self) -> Tuple[List[Dict[str, Any]], int]:
        try:
            with self.lock:
                requests_copy = self.requests.copy()

            logging.info(f"Data fetched: {requests_copy}")
            return requests_copy, 200

        except Exception as e:
            logging.error("Error retrieving requests: %s", e, exc_info=True)
            return [], 500

    def clear(self, uuid: Optional[str] = None) -> Tuple[dict, int]:
        try:
            with self.lock:
                if uuid:
                    initial_length = len(self.requests)
                    self.requests = [req for req in self.requests if req.get("uuid") != uuid]

                    if len(self.requests) == initial_length:
                        logging.info("UUID %s not found in queue.", uuid)
                        return {"error": "UUID not found"}, 404
                    else:
                        logging.info("Request with UUID %s removed.", uuid)
                        return {"status": "removed", "uuid": uuid}, 200
                else:
                    self.requests.clear()
                    logging.info("Request queue cleared successfully.")
                    return {"status": "cleared"}, 200

        except Exception as e:
            logging.error("Error clearing the request queue: %s", e, exc_info=True)
            return {"error": "Internal server error"}, 500


class App:
    def __init__(self) -> None:
        self.args = self._get_args()
        self.host = self.args.host
        self.port = self.args.port
        self.debug = self.args.debug
        self.api_key = self.args.api_key or None

        logging.info(f"API Key {'enabled' if self.api_key else 'disabled'}.")

        self.flask = Flask(__name__)
        self.flask.wsgi_app = ProxyFix(self.flask.wsgi_app, x_for=1, x_host=1, x_proto=1)

        self.request_queue = RequestQueue()

        self._setup_routes()

        logging.info(f"Server initialized on {self.host}:{self.port} (debug={self.debug})")

    def _get_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Start the Flask API server.")
        parser.add_argument("--host", type=str, default=os.getenv("HOST", "0.0.0.0"),
                            help="The host IP address on which the server will listen.")

        parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 80)),
                            help="The port number on which the server will listen.")

        parser.add_argument("--api-key", type=str, default=os.getenv("API_KEY", ""),
                            help="The API key used for authenticating incoming requests.")

        parser.add_argument("--debug", action="store_true", default=os.getenv("DEBUG", "False").lower() in {"1", "true", "yes"},
                            help="Enable debug mode for verbose logging and automatic reloads.")

        args, _ = parser.parse_known_args()

        logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        return args

    def require_api_key(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if self.api_key:
                provided_key = request.headers.get("X-API-Key")
                if provided_key != self.api_key:
                    logging.warning("Unauthorized access attempt.")
                    return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated_function

    def _setup_routes(self) -> None:
        @self.flask.route("/", methods=["GET"])
        @self.require_api_key
        def status():
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            return jsonify({
                "message": "REST API server online.",
                "client_ip": client_ip
            }), 200

        @self.flask.route("/queue", methods=["POST"])
        @self.require_api_key
        def queue_request():
            request_data = request.get_json()
            if not request_data:
                return jsonify({"error": "No request data received"}), 400
            response, status_code = self.request_queue.add(request_data)
            return jsonify(response), status_code

        @self.flask.route("/queue", methods=["GET"])
        @self.require_api_key
        def queue_get():
            response, status_code = self.request_queue.get()
            return jsonify(response), status_code

        @self.flask.route("/queue/delete", methods=["POST"])
        @self.require_api_key
        def queue_clear():
            uuid = request.args.get("uuid")
            if not uuid:
                return jsonify({"error": "UUID parameter is required"}), 400

            if uuid.lower() == "all":
                response, status_code = self.request_queue.clear()
            else:
                response, status_code = self.request_queue.clear(uuid)

            return jsonify(response), status_code


    def run(self) -> None:
        self.flask.run(host=self.host, port=self.port, debug=self.debug)


app = App().flask

if __name__ == "__main__":
    App().run()
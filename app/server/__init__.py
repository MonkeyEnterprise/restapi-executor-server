##
#
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
##

import logging
import signal
import ssl
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from server.queue import Queue
from server.routes import Routes
from server.endpoints import Endpoints

__VERSION__: str = "1.0.0"

class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000,
                 debug: bool = False, api_key: str = "",
                 ssl_cert: str = "", ssl_key: str = "") -> None:
        """Initializes the server with Flask, routing, and a command queue."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"Initializing server version {__VERSION__}")

        self.queue = Queue()
        self.app = Flask(__name__)
        self.routes = Routes(self.app)
        self.endpoints = Endpoints(self.app, self.queue)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_host=1)

        self.host = host
        self.port = port
        self.debug = debug
        
        # Load SSL certificates if provided
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.ssl_context = None
        if self.ssl_cert and self.ssl_key:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)
        elif self.ssl_cert or self.ssl_key:
            logging.error("Both ssl_cert and ssl_key must be provided for SSL. Server will not start.")
            raise ValueError("Both ssl_cert and ssl_key are required for SSL.")

        self.api_key = api_key if api_key else None
        if not self.api_key:
            logging.warning("API_KEY is not set, authentication will be disabled.")
        else:
            logging.info("API_KEY authentication enabled.")

        self._setup_routes()
        logging.info(f"Server initialized on {self.host}:{self.port} (debug={self.debug})")

    def _setup_routes(self) -> None:
        """Registers API routes via the custom `Routes` class."""
        base_url = "/api/v1"

        # Status & general endpoints
        self.routes.add(f"{base_url}", "status", self._require_api_key(self.endpoints.status), "GET")

        # Command-related endpoints
        self.routes.add(f"{base_url}/command", "add_command", self._require_api_key(self.endpoints.add_command), "POST")
        self.routes.add(f"{base_url}/commands", "clear_commands", self._require_api_key(self.endpoints.clear_commands), "DELETE")
        self.routes.add(f"{base_url}/commands", "get_commands", self._require_api_key(self.endpoints.get_commands), "GET")

    def _require_api_key(self, func):
        """Decorator to enforce API key authentication."""
        def wrapper(*args, **kwargs):
            key = request.headers.get("X-API-Key")
            if self.api_key and key != self.api_key:
                logging.warning(f"Unauthorized access attempt from {request.remote_addr}")
                return jsonify({"error": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return wrapper

    def run(self) -> None:
        """Starts the Flask server."""
        logging.info(f"Starting server on {self.host}:{self.port} (debug={self.debug})")
        
        def handle_shutdown(signum, frame):
            logging.info("Received shutdown signal, stopping server...")
            exit(0)

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        try:
            if self.ssl_context:
                self.app.run(host=self.host, port=self.port, debug=self.debug, ssl_context=self.ssl_context, threaded=True)
            else:
                self.app.run(host=self.host, port=self.port, debug=self.debug, threaded=True)  
        except Exception as e:
            logging.error(f"Unexpected error while running server: {e}", exc_info=True)

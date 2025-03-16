##
#
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
##

import logging
import signal
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from server.queue import Queue
from server.routes import Routes
from server.endpoints import Endpoints

__VERSION__: str = "1.0.0"

class Server:
    def __init__(self, host: str, port: int, debug: bool = False, api_key: str = "") -> None:
        """
        Initializes the server with Flask, routing, and a request queue.

        Args:
            host (str): The hostname or IP address to bind the server to.
            port (int): The port number to bind the server to.
            debug (bool, optional): Whether to run the server in debug mode. Defaults to False.
            api_key (str, optional): The API key for authentication. Defaults to an empty string.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"Initializing server version {__VERSION__}")

        self.queue = Queue()
        self.app = Flask(__name__)
        self.routes = Routes(self.app)
        self.endpoints = Endpoints(self.app, self.queue)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_host=1, x_proto=1)
        self.host = host
        self.port = port
        self.debug = debug
        self.api_key = api_key if api_key else None
        if not self.api_key:
            logging.warning("API_KEY is not set, authentication will be disabled.")
        else:
            logging.info("API_KEY authentication enabled.")

        self._setup_routes()
        logging.info(f"Server initialized on {self.host}:{self.port} (debug={self.debug})")

    def _setup_routes(self) -> None:
        """
        Registers API routes using the custom Routes class.

        The routes include a status endpoint as well as endpoints for managing the request queue:
            - Adding a new request
            - Clearing one or all requests
            - Listing all queued requests
        """
        base_url = "/api/v1"

        # Status & general endpoints
        self.routes.add(f"{base_url}", "status", self._require_api_key(self.endpoints.status), "GET")

        # Request-related endpoints
        self.routes.add(f"{base_url}/queue/add", "add_queue", self._require_api_key(self.endpoints.add_queue), "POST")
        self.routes.add(f"{base_url}/queue/delete", "clear_queue", self._require_api_key(self.endpoints.clear_queue), "POST")
        self.routes.add(f"{base_url}/queue/list", "get_queue", self._require_api_key(self.endpoints.get_queue), "GET")

    def _require_api_key(self, func):
        """
        Decorator to enforce API key authentication.

        Args:
            func (callable): The function to wrap with API key authentication.

        Returns:
            callable: The wrapped function which checks the provided API key against the server configuration.
        """
        def wrapper(*args, **kwargs):
            key = request.headers.get("X-API-Key")
            if self.api_key and key != self.api_key:
                logging.warning(f"Unauthorized access attempt from {request.remote_addr}")
                return jsonify({"error": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return wrapper

    def run(self) -> None:
        """
        Starts the Flask server and registers shutdown signal handlers.

        This method starts the server on the specified host and port and ensures that the server
        terminates gracefully when a shutdown signal (SIGINT or SIGTERM) is received.
        """
        logging.info(f"Starting server on {self.host}:{self.port} (debug={self.debug})")
        
        def handle_shutdown(signum, frame):
            logging.info("Received shutdown signal, stopping server...")
            exit(0)

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        try:
            self.app.run(host=self.host, port=self.port, debug=self.debug, threaded=True)
        except Exception as e:
            logging.error(f"Unexpected error while running server: {e}", exc_info=True)

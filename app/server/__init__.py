##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# This module implements a Flask-based REST API server and a thread-safe
# command queue for managing and processing commands.
##


from server.queue import Queue
from server.routes import Routes
from server.endpoints import Endpoints
from flask import Flask, request, jsonify
import logging

__VERSION__: str = "1.0.0"

class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False, api_key: str = "") -> None:
        """Initializes the server with Flask, routing, and a command queue.

        Args:
            host (str, optional): The host IP address. Defaults to "127.0.0.1".
            port (int, optional): The port number for the server. Defaults to 5000.
            debug (bool, optional): Whether to run Flask in debug mode. Defaults to False.
            api_key (str, optional): The API key for the RES API requests. Defaults to empty.
        """
        logging.info(f"Initializing server version {__VERSION__}")

        self.queue = Queue()
        self.app = Flask(__name__)
        self.routes = Routes(self.app)
        self.endpoints = Endpoints(self.app, self.queue)
        
        self.host = host
        self.port = port
        self.debug = debug
        
        self.api_key = api_key if api_key else None
        if not self.api_key:
            logging.warning("API_KEY is not set, authentication will be disabled.")
        else:
            logging.info(f"API_KEY is set to: \"{self.api_key}\", authentication is enabled.")

        self._setup_routes()

        logging.info(f"Server initialized on {self.host}:{self.port} (debug={self.debug})")

    def _setup_routes(self) -> None:
        """Registers API routes via the custom `Routes` class.

        This function defines and registers REST API endpoints 
        by mapping HTTP methods to their respective handler functions.
        """
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
                return jsonify({"error": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return wrapper

    def run(self) -> None:
        """Starts the Flask server.

        This method runs the Flask application on the specified host and port.
        It includes error handling to gracefully shutdown on keyboard interrupt.
        """
        logging.info(f"Starting server on {self.host}:{self.port} (debug={self.debug})")
        
        try:
            self.app.run(host=self.host, port=self.port, debug=self.debug)
        except KeyboardInterrupt:
            logging.info("Shutting down server gracefully.")
        except Exception as e:
            logging.error(f"Unexpected error while running server: {e}", exc_info=True)
            

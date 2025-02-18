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
from flask import Flask
import logging


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
        """Initializes the server with Flask, routing, and a command queue.

        Args:
            host (str, optional): The host IP address. Defaults to "127.0.0.1".
            port (int, optional): The port number for the server. Defaults to 5000.
            debug (bool, optional): Whether to run Flask in debug mode. Defaults to False.
        """
        logging.info("Initializing server...")

        self.queue = Queue()
        self.app = Flask(__name__)
        self.routes = Routes(self.app)
        self.endpoints = Endpoints(self.app, self.queue)
        self.host = host
        self.port = port
        self.debug = debug

        self._setup_routes()

        logging.info(f"Server initialized on {self.host}:{self.port} (debug={self.debug})")


    def _setup_routes(self) -> None:
        """Registers API routes via the custom `Routes` class.

        This function defines and registers REST API endpoints 
        by mapping HTTP methods to their respective handler functions.
        """
        base_url = "/api/v1"

        # Status & general endpoints
        self.routes.add(f"{base_url}", "status", self.endpoints.status, "GET")

        # Command-related endpoints
        self.routes.add(f"{base_url}/command", "add_command", self.endpoints.add_command, "POST")
        self.routes.add(f"{base_url}/commands", "clear_commands", self.endpoints.clear_commands, "DELETE")
        self.routes.add(f"{base_url}/commands", "get_commands", self.endpoints.get_commands, "GET") 


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


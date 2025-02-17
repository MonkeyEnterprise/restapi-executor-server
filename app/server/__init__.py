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
    """
    Example: >> curl -X POST http://localhost:5000/api/v1/addCommand -H "Content-Type: application/json" -d "{\"endpoint\":\"test\"}"
    """    
    
    API_BASE_URL: str = '/api/v1'
    API_CLIENT_RESPONSE: str = "clientResponse"
    API_ADD_COMMAND: str = "addCommand"
    API_GET_COMMANDS: str = "getCommands"
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
        self.queue = Queue()
        self.app = Flask(__name__)
        self.routes = Routes(self.app)
        self.endpoints = Endpoints(self.app, self.queue)
        self.host = host
        self.port = port
        self.debug = debug
        
        self._setup_routes()

    def _setup_routes(self) -> None:
        """
        Registreert de routes via de custom Routes-klasse, zodat deze
        direct worden gekoppeld aan de Flask-applicatie.
        """
        self.routes.add(f"{self.API_BASE_URL}",
                        "status",
                        self.endpoints.status,
                        "GET")
        
        self.routes.add(f"{self.API_BASE_URL}/{self.API_CLIENT_RESPONSE}/<command_id>",
                        "get_client_response",
                        self.endpoints.get_client_response,
                        "GET")
        
        self.routes.add(f"{self.API_BASE_URL}/{self.API_ADD_COMMAND}",
                        "add_command",
                        self.endpoints.add_command,
                        "POST")   
            
        self.routes.add(f"{self.API_BASE_URL}/{self.API_GET_COMMANDS}",
                        "get_commands",
                        self.endpoints.get_commands,
                        "GET")

        # self.routes.add("/api/v1/updateStatus", "update_status", self.update_status, "POST")

    def run(self) -> None:
        logging.info(f"Starting server on {self.host}:{self.port} (debug={self.debug})")
        self.app.run(host=self.host, port=self.port, debug=self.debug)

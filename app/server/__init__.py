from flask import Flask
import logging
import os
import argparse
from werkzeug.middleware.proxy_fix import ProxyFix
from .RequestQueue import RequestQueue
from .ApiRoutes import ApiRoutes

class App:
    
    CONFIG_KEY_REQUEST_QUEUE = "REQUEST_QUEUE"
    CONFIG_KEY_API_KEY = "API_KEY"
    
    def __init__(self) -> None:
        self.args = self._get_args()
        self.host = self.args.host
        self.port = self.args.port
        self.debug = self.args.debug
        self.api_key = self.args.api_key or None

        logging.info(f"API Key {'enabled' if self.api_key else 'disabled'}.")

        self.flask = Flask(__name__)
        self.flask.wsgi_app = ProxyFix(self.flask.wsgi_app, x_for=1, x_host=1, x_proto=1)

        self.flask.config[self.CONFIG_KEY_API_KEY] = self.api_key
        self.flask.config[self.CONFIG_KEY_REQUEST_QUEUE] = RequestQueue()

        ApiRoutes(self.flask)

        logging.info(f"Server initialized on {self.host}:{self.port} (debug={self.debug})")

    def _get_args(self):
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

    def run(self) -> None:
        self.flask.run(host=self.host, port=self.port, debug=self.debug)

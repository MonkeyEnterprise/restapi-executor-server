##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# This module implements a Flask-based REST API server and a thread-safe
# command queue for managing and processing commands.
##


from flask import Flask
from server import Server
import logging
import os
import argparse

def get_args() -> argparse.Namespace:
    """Parses command-line arguments for configuring the Flask server.

    Returns:
        argparse.Namespace: An object containing parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Start the Flask API server.")
    
    parser.add_argument("--host", type=str, default=os.environ.get("HOST", "127.0.0.1"), help="Host IP address")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 80)), help="Port number")
    parser.add_argument("--api_key", type=str, default=os.getenv("API_KEY", ""), help="API key")
        
    debug_env = os.environ.get("DEBUG", "False").lower()
    debug_default = debug_env in {"1", "true", "yes"}
    
    parser.add_argument("--debug", action="store_true", default=debug_default, help="Enable debug mode")
    
    args, _ = parser.parse_known_args()
    
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, 
                        format="%(asctime)s - %(levelname)s - %(message)s")

    return args

def gunicorn_server() -> "Flask":
    """Initializes and returns a Flask application for use with Gunicorn.

    Returns:
        Flask: A Flask application instance.
    """
    args = get_args()
    server = Server(host=args.host, port=args.port, debug=args.debug, api_key=args.api_key)
    return server.app

if __name__ == "__main__":
    # Running the script directly: Start the Flask server with command-line arguments.
    args = get_args()
    server = Server(host=args.host, port=args.port, debug=args.debug, api_key=args.api_key)
    server.run()
else:
    # Importing this module elsewhere or running via Gunicorn: Expose the Flask app instance.
    app = gunicorn_server()

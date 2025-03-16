##
#
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
##

from flask import Flask
from server import Server
import logging
import os
import argparse

def get_args() -> argparse.Namespace:
    """
    Parse command-line arguments and environment variables for configuring the Flask API server.

    This function uses argparse to collect command-line parameters such as host, port, API key,
    and debug mode. Indien niet expliciet opgegeven, worden standaardwaarden gebruikt uit de
    omgeving variabelen.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Start the Flask API server.")
    
    parser.add_argument("--host",
                        type=str,
                        default=os.getenv("HOST", "0.0.0.0"),
                        help="The host IP address on which the server will listen.")
    
    parser.add_argument("--port",
                        type=int,
                        default=int(os.getenv("PORT", 80)),
                        help="The port number on which the server will listen.")
    
    parser.add_argument("--api_key",
                        type=str,
                        default=os.getenv("API_KEY", ""),
                        help="The API key used for authenticating incoming requests.")
    
    debug_env = os.getenv("DEBUG", "False").lower()
    debug_default = debug_env in {"1", "true", "yes"}
    parser.add_argument("--debug",
                        action="store_true",
                        default=debug_default,
                        help="Enable debug mode for verbose logging and automatic reloads.")
    
    args, _ = parser.parse_known_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    return args

def gunicorn_server() -> Flask:
    """
    Initialize and return a Flask application instance for use with Gunicorn.

    This function creates a Server instance using the parsed configuration parameters and returns
    the underlying Flask application. This is useful when running the application with a WSGI server
    like Gunicorn.

    Returns:
        Flask: A configured Flask application instance.
    """
    args = get_args()
    server = Server(host=args.host, port=args.port, debug=args.debug, api_key=args.api_key)
    return server.app

if __name__ == "__main__":
    # When this module is executed directly, start the Flask server using the parsed command-line arguments.
    args = get_args()
    server = Server(host=args.host, port=args.port, debug=args.debug, api_key=args.api_key)
    server.run()
else:
    # When imported (e.g. by Gunicorn), expose the Flask app instance.
    app = gunicorn_server()

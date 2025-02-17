##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# This module implements a Flask-based REST API server and a thread-safe
# command queue for managing and processing commands.
##

from modules import *
import logging
import os
import argparse


def get_args():
    """
    Parses command-line arguments for configuring the Flask server.

    Returns:
        argparse.Namespace: An object containing parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Start the Flask API server.", 
        add_help=False  # Disable help to avoid conflicts with Gunicorn's arguments.
    )
    parser.add_argument("--host", type=str, default=os.environ.get("HOST", "0.0.0.0"), help="Host IP address")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)), help="Port number")
    parser.add_argument("--debug", action="store_true", default=os.environ.get("DEBUG", "False").lower() == "true", help="Enable debug mode")
    args, _ = parser.parse_known_args()  # Ignore any unknown arguments.
    return args


def gunicorn_server():
    """
    Initializes and returns a Flask application for use with Gunicorn.

    Returns:
        Flask: A Flask application instance.
    """
    args = get_args()
    server = RestAPIServer(host=args.host, port=args.port, debug=args.debug)
    return server.app


if __name__ == "__main__":
    # Running the script directly: Start the Flask server with command-line arguments.
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    args = get_args()
    server = RestAPIServer(host=args.host, port=args.port, debug=args.debug)
    server.run()
else:
    # Importing this module elsewhere or running via Gunicorn: Expose the Flask app instance.
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    app = gunicorn_server()

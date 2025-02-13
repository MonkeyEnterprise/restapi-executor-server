##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# This module implements a Flask-based REST API server and a thread-safe
# command queue for managing and processing commands.
##


from flask import Flask, request, jsonify, Response
import threading
import uuid
import logging
import os
import argparse


class CommandQueue:
    """
    A thread-safe queue for managing commands and their responses.

    This class provides methods to enqueue commands, retrieve queued commands,
    update command statuses, and fetch responses.
    """

    def __init__(self) -> None:
        """
        Initializes the CommandQueue with a command queue, response storage, and a thread lock.
        """
        self.commands = []
        self.responses = {}
        self.lock = threading.Lock()

    def get_commands(self) -> list[dict]:
        """
        Retrieves and clears all queued commands.

        Returns:
            list[dict]: A list of command dictionaries.
        """
        try:
            with self.lock:
                commands = self.commands.copy()
                self.commands.clear()
            logging.info("Fetched and cleared the command queue.")
            return commands
        except Exception as e:
            logging.error("Error retrieving commands: %s", e, exc_info=True)
            return []

    def enqueue_command(self, command: dict) -> tuple[dict, int]:
        """
        Adds a new command to the queue and initializes its response.

        Args:
            command (dict): The command to enqueue. Must contain an 'endpoint' key.

        Returns:
            tuple[dict, int]: A JSON response indicating success or failure, along with an HTTP status code.
        """
        try:
            if not isinstance(command, dict) or "endpoint" not in command:
                logging.error("Invalid command format: %s", command)
                return {"error": "Invalid command format"}, 400

            command_id = str(uuid.uuid4())  # Generate a unique command ID
            command["id"] = command_id

            with self.lock:
                self.commands.append(command)
                self.responses[command_id] = None

            logging.info("Command queued: %s", command)
            return {"status": "queued", "command_id": command_id}, 200
        except Exception as e:
            logging.error("Error enqueuing command: %s", e, exc_info=True)
            return {"error": "Internal server error"}, 500

    def update_status(self, status: dict) -> tuple[dict, int]:
        """
        Updates the response status of a command.

        Args:
            status (dict): A dictionary containing the command ID and status update.

        Returns:
            tuple[dict, int]: A JSON response indicating success or failure, along with an HTTP status code.
        """
        try:
            command_id = status.get("command", {}).get("id")
            if not command_id:
                logging.error("Invalid status update format: %s", status)
                return {"error": "Invalid status update format"}, 400

            with self.lock:
                if command_id not in self.responses:
                    logging.error("Command ID not found: %s", command_id)
                    return {"error": "Command ID not found"}, 404
                self.responses[command_id] = status

            logging.info("Received status update for %s: %s", command_id, status)
            return {"status": "received"}, 200
        except Exception as e:
            logging.error("Error updating status: %s", e, exc_info=True)
            return {"error": "Internal server error"}, 500

    def get_response(self, command_id: str) -> tuple[dict, int]:
        """
        Retrieves the response for a given command ID.

        Args:
            command_id (str): The command ID to retrieve the response for.

        Returns:
            tuple[dict, int]: A JSON response containing the command's result, or an error message if unavailable.
        """
        try:
            with self.lock:
                response = self.responses.get(command_id)
            
            if response is not None:
                logging.info("Response retrieved for command ID %s: %s", command_id, response)
                return response, 200

            logging.warning("Response not available yet for command ID %s", command_id)
            return {"error": "Response not available yet"}, 404
        except Exception as e:
            logging.error("Error retrieving response for %s: %s", command_id, e, exc_info=True)
            return {"error": "Internal server error"}, 500


class RestAPIServer:
    """
    A Flask-based REST API server for handling command execution.

    This server provides endpoints to enqueue commands, fetch pending commands, 
    update command statuses, and retrieve responses.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
        """
        Initializes the REST API server with a Flask application.

        Args:
            host (str, optional): The host IP address. Defaults to "127.0.0.1".
            port (int, optional): The port number. Defaults to 5000.
            debug (bool, optional): Whether to run the server in debug mode. Defaults to False.
        """
        self.queue = CommandQueue()  # Ensure CommandQueue is defined/imported elsewhere
        self.host = host
        self.port = port
        self.debug = debug
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self) -> None:
        """
        Defines API endpoints and associates them with handler functions.
        """
        self.app.add_url_rule("/api/v1", "get_status", self.get_status, methods=["GET"])
        self.app.add_url_rule("/api/v1/callsToExecute", "get_commands", self.get_commands, methods=["GET"])
        self.app.add_url_rule("/api/v1/enqueueCommand", "enqueue_command", self.enqueue_command, methods=["POST"])
        self.app.add_url_rule("/api/v1/getResponse/<command_id>", "get_response", self.get_response, methods=["GET"])
        self.app.add_url_rule("/api/v1/updateStatus", "update_status", self.update_status, methods=["POST"])

    def get_commands(self) -> Response:
        """
        Fetches and clears all queued commands.

        Returns:
            Response: A JSON list of queued commands.
        """
        logging.debug("get_commands called to fetch and clear all queued commands")
        try:
            commands = self.queue.get_commands()
            logging.debug("Retrieved commands: %s", commands)
        except Exception as e:
            logging.error("Error fetching commands: %s", e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully fetched and cleared queued commands")
        return jsonify(commands)

    def enqueue_command(self) -> Response:
        """
        Adds a new command to the queue.

        Returns:
            Response: A JSON object containing the command ID and status.
        """
        logging.debug("enqueue_command called with payload: %s", request.json)
        try:
            data, status = self.queue.enqueue_command(request.json)
            logging.debug("Queue.enqueue_command returned data: %s with status: %s", data, status)
        except Exception as e:
            logging.error("Error enqueuing command with payload %s: %s", request.json, e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully enqueued command.")
        return jsonify(data), status

    def update_status(self) -> Response:
        """
        Updates the execution status of a command.

        Returns:
            Response: A JSON object indicating success or failure.
        """
        logging.debug("update_status called with payload: %s", request.json)
        try:
            data, status = self.queue.update_status(request.json)
            logging.debug("Queue.update_status returned data: %s with status: %s", data, status)
        except Exception as e:
            logging.error("Error updating status with payload %s: %s", request.json, e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully updated status.")
        return jsonify(data), status

    def get_response(self, command_id: str) -> Response:
        """
        Retrieves the response for a specific command.

        Args:
            command_id (str): The unique identifier of the command.

        Returns:
            Response: A JSON object containing the command response.
        """
        logging.debug("get_response called with command_id: %s", command_id)
        try:
            data, status = self.queue.get_response(command_id)
            logging.debug("Queue returned data: %s with status: %s", data, status)
        except Exception as e:
            logging.error("Error retrieving response for command_id %s: %s", command_id, e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully retrieved response for command_id: %s", command_id)
        return jsonify(data), status

    def get_status(self) -> Response:
        """
        Provides a simple health check endpoint.

        Returns:
            Response: A JSON object indicating server health.
        """
        logging.debug("Entered get_status endpoint.")
        logging.info("Health check endpoint called.")
        response = jsonify({"message": "You are successfully connected to the REST API server."})
        logging.debug("Exiting get_status endpoint with response: %s", response)
        return response, 200

    def run(self) -> None:
        """
        Starts the Flask API server.
        """
        logging.info(f"Starting server on {self.host}:{self.port} (debug={self.debug})")
        self.app.run(host=self.host, port=self.port, debug=self.debug)


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
    parser.add_argument("--host", type=str, default=os.environ.get("HOST", "127.0.0.1"), help="Host IP address")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 80)), help="Port number")
    parser.add_argument("--debug", action="store_true", default=os.environ.get("DEBUG", "False").lower() == "true", help="Enable debug mode")
    args, _ = parser.parse_known_args()  # Ignore any unknown arguments.
    return args

def gunicorn_server() -> Flask:
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

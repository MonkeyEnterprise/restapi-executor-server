##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# This module implements a Flask-based REST API server and a thread-safe
# command queue for managing and processing commands.
##

from .command_queue import CommandQueue
from flask import Flask, request, jsonify, Response
import logging


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

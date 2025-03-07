##
#
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
##

from .queue import Queue
from flask import Flask, request, jsonify, Response
import logging

class Endpoints:
    """Defines API endpoints for a Flask application."""

    def __init__(self, app: Flask, queue: Queue) -> None:
        """Initializes the Endpoints class with a Flask application instance.

        Args:
            app (Flask): The Flask application instance.
            queue (Queue): The queue instance responsible for managing command responses.
        """
        self.app = app
        self.queue = queue

    def status(self) -> tuple[Response, int]:
        """Handles the status check endpoint."""
        try:
            logging.debug("Entered status endpoint.")
            logging.info("Status check endpoint called.")
            client_ip = request.remote_addr
            response = jsonify({
                "message": "You are successfully connected to the REST API server.",
                "client_ip": client_ip
            })
            logging.debug("Exiting status endpoint with response: %s", response.get_json())
            return response, 200

        except Exception as e:
            logging.error("Error in status endpoint: %s", e, exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    def add_command(self) -> Response:
        """Adds a command to the queue."""
        logging.debug("add_command called with payload: %s", request.json)
        try:
            data, status = self.queue.add(request.json)
            logging.debug("Queue.add returned data: %s with status: %s", data, status)
        except Exception as e:
            logging.error("Error adding command with payload %s: %s", request.json, e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully added command.")
        return jsonify(data), status

    def get_commands(self) -> tuple[Response, int]:
        """Fetches and clears all queued commands."""
        logging.debug("get_commands called to fetch and clear all queued commands")
        try:
            commands = self.queue.fetch()
            if not commands:
                logging.warning("No commands found in queue.")
                commands = []
            logging.debug("Retrieved %d commands: %s", len(commands), commands)
        except Exception as e:
            logging.error("Error fetching commands: %s", e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully fetched queued commands")
        return jsonify(commands), 200

    def clear_command(self) -> tuple[Response, int]:
        """Clears a specific command from the queue if UUID is provided, otherwise returns an error."""
        logging.debug("clear_command called to remove a queued command")

        try:
            # Ensure JSON body exists before accessing it
            if not request.is_json:
                logging.warning("Request body is missing or not JSON.")
                return jsonify({"error": "Request body must be JSON"}), 400

            uuid = request.json.get("uuid")

            if not uuid:
                logging.warning("Clear command failed: UUID is required.")
                return jsonify({"error": "UUID is required"}), 400

            # Attempt to clear the command with the given UUID
            if self.queue.clear(uuid):  # Updated to return success status
                logging.info("Successfully removed command with UUID: %s", uuid)
                return jsonify({"message": f"Successfully removed command with UUID {uuid}"}), 200
            else:
                logging.warning("UUID %s not found in queue.", uuid)
                return jsonify({"error": "UUID not found in queue"}), 404

        except Exception as e:
            logging.error("Error clearing commands: %s", e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

    def clear_commands(self) -> tuple[Response, int]:
        """Clears all queued commands from the queue."""
        logging.debug("clear_commands called to remove all queued commands")
        try:
            self.queue.clear()
            logging.info("Successfully cleared the queued commands")
            return jsonify({"message": "Successfully cleared the queued commands"}), 200
        except Exception as e:
            logging.error("Error clearing commands: %s", e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

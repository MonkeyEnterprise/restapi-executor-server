from .queue import Queue  # Import your custom Queue, not the built-in one
from flask import Flask, request, jsonify, Response
import logging

class Endpoints:
    """Defines API endpoints for the Flask application."""

    def __init__(self, app: Flask, queue: Queue) -> None:
        """Initializes the Endpoints class with a Flask application instance.

        Args:
            app (Flask): The Flask application instance.
            queue (Queue): The queue instance responsible for managing command responses.
        """
        self.app = app
        self.queue = queue
       
    def status(self) -> tuple[Response, int]:
        """Handles the status check endpoint.

        This endpoint returns a success message along with the 
        client's IP address, indicating that the REST API server is reachable.

        Returns:
            tuple[Response, int]: A JSON response with a success message, 
            the client's IP address, and HTTP status 200.
        """
        try:
            logging.debug("Entered status endpoint.")
            logging.info("Status check endpoint called.")

            client_ip = request.remote_addr  # Get client IP address

            response = jsonify({
                "message": "You are successfully connected to the REST API server.",
                "client_ip": client_ip
            })

            logging.debug("Exiting status endpoint with response: %s", response.get_json())
            return response, 200

        except Exception as e:
            logging.error("Error in status endpoint: %s", e, exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    def get_client_response(self, command_id: str) -> tuple[Response, int]:
        """Retrieves the client response associated with a given command ID.

        Args:
            command_id (str): The unique identifier of the command.

        Returns:
            tuple[Response, int]: A JSON response containing the command result 
            and the associated HTTP status code.

        Raises:
            Exception: Logs and handles unexpected errors gracefully.
        """
        logging.debug("get_client_response called with command_id: %s", command_id)
        
        try:
            data, status = self.queue.get_response(command_id)
            logging.debug("Queue returned data: %s with status: %s", data, status)
        except Exception as e:
            logging.error("Error retrieving response for command_id %s: %s", command_id, e, exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

        logging.info("Successfully retrieved client response for command_id: %s", command_id)
        return jsonify(data), status

    def add_command(self) -> Response:
        """Adds a command to the queue.

        This endpoint processes a JSON request and adds a command 
        to the queue.

        Returns:
            Response: A JSON response containing the queued command status.
        """
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
        """Fetches and clears all queued commands.

        This endpoint retrieves all stored commands from the queue and clears it.
        If no commands are available, an empty list is returned.

        Returns:
            tuple[Response, int]: A JSON response containing the list of commands 
            and HTTP status 200. If an error occurs, it returns an error response with HTTP 500.
        """
        logging.debug("get_commands called to fetch and clear all queued commands")

        try:
            commands = self.queue.fetch()

            if not commands:  # Handles None or empty case
                logging.warning("No commands found in queue.")
                commands = []

            logging.debug("Retrieved %d commands: %s", len(commands), commands)

        except Exception as e:
            logging.error("Error fetching commands: %s", e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        self.queue.clear()
        
        logging.info("Successfully fetched and cleared queued commands")
        return jsonify(commands), 200  # Explicitly returning HTTP 200


    # def update_status(self) -> Response:
    #     logging.debug("update_status called with payload: %s", request.json)
    #     try:
    #         data, status = self.queue.update_status(request.json)
    #         logging.debug("Queue.update_status returned data: %s with status: %s", data, status)
    #     except Exception as e:
    #         logging.error("Error updating status with payload %s: %s", request.json, e, exc_info=True)
    #         return jsonify({"error": "Internal Server Error"}), 500

    #     logging.info("Successfully updated status.")
    #     return jsonify(data), status




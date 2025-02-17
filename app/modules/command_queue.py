##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# command queue for managing and processing commands.
##


import threading
import uuid
import logging


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
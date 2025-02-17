##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# Command queue for managing and processing commands.
##

from typing import Dict, List, Optional
import threading
import uuid
import logging


class Queue:    
    
    ENDPOINT_NAME: str = 'endpoint'

    def __init__(self) -> None:
        self.commands: List[Dict] = []
        self.responses: Dict[str, Optional[Dict]] = {}
        self.lock: threading.Lock = threading.Lock()
        

    def fetch(self) -> list[dict]:
        """Retrieves the command queue.

        This method safely accesses the command queue using a lock, retrieves
        a copy of the commands and logs the operation.

        Returns:
            list[dict]: A list of command dictionaries that were in the queue.
            If an error occurs, an empty list is returned.
        """
        try:
            with self.lock:
                commands = self.commands.copy()
            logging.debug(f"Data fetched and queue cleared: {commands}")
            logging.info("Fetched and cleared the command queue.")
            return commands
        except Exception as e:
            logging.error("Error retrieving commands: %s", e, exc_info=True)
            return []

    def clear(self) -> None:
        """Clears the command queue.

        This method attempts to remove all stored commands from the queue safely
        using a lock. If an error occurs, it logs the exception.
        """
        try:
            with self.lock:
                self.commands.clear()
            logging.info("Command queue cleared successfully.")
        except Exception as e:
            logging.error("Error clearing the command queue: %s", e, exc_info=True)

    def add(self, command: dict) -> tuple[dict, int]:
        """Adds a command to the queue with a unique ID.

        This method validates the command format, assigns a unique ID, and 
        adds it to the command queue. If the command is not a dictionary, 
        it logs an error and raises a TypeError. If the command is missing 
        the required `ENDPOINT_NAME` key, it returns an error response.

        Args:
            command (dict): The command to be added to the queue.

        Returns:
            tuple[dict, int]: 
                - If successful, returns a dictionary with the command status 
                  and its unique ID, along with HTTP status 200.
                - If the command format is invalid, returns an error message 
                  and HTTP status 400.
                - If an unexpected error occurs, returns a generic error 
                  message and HTTP status 500.

        Raises:
            TypeError: If the provided command is not a dictionary.
        """
        if not isinstance(command, dict):
            error_message = f"Error: the command of type {type(command)} is not valid. Expected dict."
            logging.error("Error adding the command: %s", error_message, exc_info=True)
            raise TypeError(error_message)

        try:
            if self.ENDPOINT_NAME not in command:
                logging.error("Invalid command format: %s", command)
                return {"error": "Invalid command format"}, 400

            command_id = str(uuid.uuid4())
            command["id"] = command_id

            with self.lock:
                self.commands.append(command)
                self.responses[command_id] = None

            logging.info("Command queued: %s", command)
            return {"status": "queued", "command_id": command_id}, 200

        except Exception as e:
            logging.exception("Error enqueuing command")
            return {"error": "Internal server error"}, 500

    def update_status(self, status: dict) -> tuple[dict, int]:
        """Updates the status of a command in the response queue.

        This method checks if the provided status update is a dictionary, extracts 
        the `command_id` from the nested "command" field, and updates the status 
        in the response queue. It ensures thread-safe access using a lock.

        Args:
            status (dict): A dictionary containing the command's updated status.
                           The expected format includes a nested "command" dict 
                           with an "id" key.

        Returns:
            tuple[dict, int]: 
                - If successful, returns a confirmation message with HTTP status 200.
                - If the input format is incorrect, returns an error message with HTTP status 400.
                - If the command ID is not found, returns an error message with HTTP status 404.
                - If an unexpected error occurs, returns a generic error message with HTTP status 500.

        Raises:
            TypeError: If the provided status is not a dictionary.
        """
        if not isinstance(status, dict):
            error_message = f"Error: the status of type {type(status)} is not valid. Expected dict."
            logging.error("Error updating status: %s", error_message, exc_info=True)
            raise TypeError(error_message)

        try:
            # Extract command ID from the nested "command" dictionary
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
        except Exception:
            logging.exception("Error updating status")
            return {"error": "Internal server error"}, 500

    def get_response(self, command_id: str) -> tuple[dict, int]:
        """Retrieves the response for a given command ID.

        This method checks if a response exists for the specified `command_id`. 
        If a response is available, it is returned with HTTP status 200. 
        If the response is not yet available, an error message is returned with HTTP status 202.

        Args:
            command_id (str): The unique identifier of the command whose response is requested.

        Returns:
            tuple[dict, int]: 
                - If the response exists, returns the response dictionary and HTTP status 200.
                - If the response is not available, returns an error message and HTTP status 202.
                - If an unexpected error occurs, returns a generic error message and HTTP status 500.
        """
        try:
            with self.lock:
                response = self.responses.get(command_id)
            
            if response is not None:
                logging.info("Response retrieved for command ID %s: %s", command_id, response)
                return response, 200

            logging.warning("Response not available yet for command ID %s", command_id)
            return {"error": "Response not available yet"}, 202
        except Exception:
            logging.exception("Error retrieving response for command ID %s", command_id)
            return {"error": "Internal server error"}, 500

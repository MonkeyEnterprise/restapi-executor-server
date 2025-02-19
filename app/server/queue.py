##
#
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
##


from typing import Dict, List
import threading
import uuid
import logging

class Queue:
    """Defines queue lists for a Flask application."""
    def __init__(self) -> None:
        self.commands: List[Dict] = []
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
        it logs an error and raises a TypeError.

        Args:
            command (dict): The command to be added to the queue.

        Returns:
            tuple[dict, int]: 
                - If successful, returns a dictionary with the command status 
                  and its unique ID, along with HTTP status 200.
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
            unique_id:str = str(uuid.uuid4())
            command["uuid"] = unique_id

            with self.lock:
                self.commands.append(command)
                # self.responses[unique_id] = None

            logging.info("Command queued: %s", command)
            return {"status": "queued", "uuid": unique_id}, 200

        except Exception as e:
            logging.exception("Error enqueuing command")
            return {"error": "Internal server error"}, 500
        

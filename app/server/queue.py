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
        """Initializes the Queue with an empty command list and a threading lock."""
        self.commands: List[Dict] = []
        self.lock: threading.Lock = threading.Lock()

    def fetch(self) -> List[Dict]:
        """Retrieves the command queue.

        Returns:
            List[Dict]: A list of command dictionaries that were in the queue.
        """
        try:
            with self.lock:
                commands = self.commands.copy()
                
            logging.debug(f"Data fetched: {commands}")
            logging.info("Fetched and cleared the command queue.")
            return commands
        
        except Exception as e:
            logging.error("Error retrieving commands: %s", e, exc_info=True)
            return []

    def clear(self, uuid: str = None) -> bool:
        """Clears the command queue or removes a specific command by UUID.

        Args:
            uuid (str, optional): The UUID of the command to remove. If None, clears the entire queue.

        Returns:
            bool: True if the queue was cleared or the command was removed, False otherwise.
        """
        try:
            with self.lock:
                if uuid:
                    initial_length = len(self.commands)
                    self.commands = [cmd for cmd in self.commands if cmd.get("uuid") != uuid]

                    if len(self.commands) == initial_length:
                        logging.warning("UUID %s not found in queue.", uuid)
                        return False
                    else:
                        logging.info("Command with UUID %s removed.", uuid)
                        return True
                else:
                    self.commands.clear()
                    logging.info("Command queue cleared successfully.")
                    return True

        except Exception as e:
            logging.error("Error clearing the command queue: %s", e, exc_info=True)
            return False

    def add(self, command: Dict) -> tuple[Dict, int]:
        """Adds a command to the queue with a unique ID.

        Args:
            command (Dict): The command to be added.

        Returns:
            tuple[Dict, int]: A tuple containing the command status and HTTP status code.

        Raises:
            TypeError: If the command is not a dictionary.
        """
        if not isinstance(command, dict):
            error_message = f"Error: Expected dict, but got {type(command).__name__}."
            logging.error(error_message)
            raise TypeError(error_message)

        try:
            unique_id: str = str(uuid.uuid4())
            command["uuid"] = unique_id

            with self.lock:
                self.commands.append(command)

            logging.info("Command queued successfully: %s", command)
            logging.debug("Current queue state: %s", self.commands)
            return {"status": "queued", "uuid": unique_id}, 200

        except Exception as e:
            logging.exception("Error enqueuing command")
            return {"error": "Internal server error"}, 500

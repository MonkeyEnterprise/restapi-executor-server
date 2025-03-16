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
    """Defines a request queue for a Flask application."""
    
    def __init__(self) -> None:
        """Initializes the request queue with an empty list and a threading lock."""
        self.requests: List[Dict] = []
        self.lock: threading.Lock = threading.Lock()

    def fetch(self) -> List[Dict]:
        """Retrieves the request queue.

        Returns:
            List[Dict]: A list of request dictionaries that were in the queue.
        """
        try:
            with self.lock:
                requests_copy = self.requests.copy()
                
            logging.debug(f"Data fetched: {requests_copy}")
            logging.info("Fetched the request queue.")
            return requests_copy
        
        except Exception as e:
            logging.error("Error retrieving requests: %s", e, exc_info=True)
            return []

    def clear(self, uuid: str = None) -> bool:
        """Clears the request queue or removes a specific request by UUID.

        Args:
            uuid (str, optional): The UUID of the request to remove. If None, clears the entire queue.

        Returns:
            bool: True if the queue was cleared or the request was removed, False otherwise.
        """
        try:
            with self.lock:
                if uuid:
                    initial_length = len(self.requests)
                    self.requests = [req for req in self.requests if req.get("uuid") != uuid]

                    if len(self.requests) == initial_length:
                        logging.warning("UUID %s not found in queue.", uuid)
                        return False
                    else:
                        logging.info("Request with UUID %s removed.", uuid)
                        return True
                else:
                    self.requests.clear()
                    logging.info("Request queue cleared successfully.")
                    return True

        except Exception as e:
            logging.error("Error clearing the request queue: %s", e, exc_info=True)
            return False

    def add(self, request_data: Dict) -> tuple[Dict, int]:
        """Adds a request to the queue with a unique ID.

        Args:
            request_data (Dict): The request data to be added.

        Returns:
            tuple[Dict, int]: A tuple containing the request status and HTTP status code.

        Raises:
            TypeError: If the request data is not a dictionary.
        """
        if not isinstance(request_data, dict):
            error_message = f"Error: Expected dict, but got {type(request_data).__name__}."
            logging.error(error_message)
            raise TypeError(error_message)

        try:
            unique_id: str = str(uuid.uuid4())
            request_data["uuid"] = unique_id

            with self.lock:
                self.requests.append(request_data)

            logging.info("Request queued successfully: %s", request_data)
            logging.debug("Current queue state: %s", self.requests)
            return {"status": "queued", "uuid": unique_id}, 200

        except Exception as e:
            logging.exception("Error enqueuing request")
            return {"error": "Internal server error"}, 500

import logging
import uuid
import threading
from typing import Optional, Tuple, Dict, Any, List

class RequestQueue:
    def __init__(self) -> None:
        self.requests: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def add(self, request_data: dict) -> Tuple[dict, int]:
        if not isinstance(request_data, dict):
            logging.error(f"Expected dict, but got {type(request_data).__name__}")
            return {"error": "Invalid request data"}, 400

        try:
            unique_id = str(uuid.uuid4())
            request_data["uuid"] = unique_id

            with self.lock:
                self.requests.append(request_data)

            logging.info("Request queued successfully: %s", request_data)
            return {"status": "queued", "uuid": unique_id}, 200

        except Exception as e:
            logging.exception("Error enqueuing request")
            return {"error": "Internal server error"}, 500

    def get(self) -> Tuple[List[Dict[str, Any]], int]:
        try:
            with self.lock:
                requests_copy = self.requests.copy()

            logging.info(f"Data fetched: {requests_copy}")
            return requests_copy, 200

        except Exception as e:
            logging.error("Error retrieving requests: %s", e, exc_info=True)
            return [], 500

    def clear(self, uuid: Optional[str] = None) -> Tuple[dict, int]:
        try:
            with self.lock:
                if uuid:
                    initial_length = len(self.requests)
                    self.requests = [req for req in self.requests if req.get("uuid") != uuid]

                    if len(self.requests) == initial_length:
                        logging.info("UUID %s not found in queue.", uuid)
                        return {"error": "UUID not found"}, 404
                    else:
                        logging.info("Request with UUID %s removed.", uuid)
                        return {"status": "removed", "uuid": uuid}, 200
                else:
                    self.requests.clear()
                    logging.info("Request queue cleared successfully.")
                    return {"status": "cleared"}, 200

        except Exception as e:
            logging.error("Error clearing the request queue: %s", e, exc_info=True)
            return {"error": "Internal server error"}, 500
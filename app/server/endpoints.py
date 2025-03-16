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
    """
    A class to define and manage API endpoints for a Flask application.

    This class registers and handles various REST API endpoints, interacting with
    a request queue to manage incoming requests and responses.
    """

    def __init__(self, app: Flask, queue: Queue) -> None:
        """
        Initialize the Endpoints instance.

        Args:
            app (Flask): The Flask application instance where endpoints will be registered.
            queue (Queue): The queue instance used to manage incoming requests and responses.
        """
        self.app = app
        self.queue = queue

    def status(self) -> tuple[Response, int]:
        """
        Status endpoint to verify API connectivity.

        This endpoint returns a JSON response confirming that the connection to the API server is successful.
        It also provides the client's IP address and name (if available).

        Returns:
            tuple[Response, int]: A tuple containing a JSON response with a success message, client IP, and client name,
                                  along with the HTTP status code 200 on success.
        """
        try:
            logging.debug("Entered status endpoint.")
            logging.info("Status check endpoint called.")
            client_ip = request.headers.get('X-Header-IP', request.remote_addr)
            client_name = request.headers.get('X-Client-Name', 'Unknown')
            response = jsonify({
                "message": "You are successfully connected to the REST API server.",
                "client_ip": client_ip,
                "client_name": client_name
            })
            logging.debug("Exiting status endpoint with response: %s", response.get_json())
            return response, 200

        except Exception as e:
            logging.error("Error in status endpoint: %s", e, exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    def get_queue(self) -> tuple[Response, int]:
        """
        Retrieve all requests from the queue.

        This endpoint fetches all queued incoming requests. If the queue is empty,
        it returns an empty list. All operations are logged, and any errors during
        the process result in an appropriate error response.

        Returns:
            tuple[Response, int]: A tuple containing a JSON response with the list of queued requests
                                  and the corresponding HTTP status code.
        """
        logging.debug("get_queue called to fetch and clear all queued requests")
        try:
            queue_list = self.queue.fetch()
            if not queue_list:
                logging.warning("No requests found in queue.")
                queue_list = []
            logging.debug("Retrieved %d requests: %s", len(queue_list), queue_list)
            
        except Exception as e:
            logging.error("Error fetching requests: %s", e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully fetched queued requests")
        return jsonify(queue_list), 200

    def add_queue(self) -> Response:
        """
        Add a new request to the queue.

        This endpoint reads a JSON payload from the incoming request and adds it to the request queue.
        It logs both the input payload and the result of the operation.

        Returns:
            Response: A JSON response with the outcome of the add operation and an appropriate HTTP status code.
        """
        logging.debug("add_queue called with payload: %s", request.json)
        try:
            data, status = self.queue.add(request.json)
            logging.debug("Queue.add returned data: %s with status: %s", data, status)
            
        except Exception as e:
            logging.error("Error adding request with payload %s: %s", request.json, e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

        logging.info("Successfully added request.")
        return jsonify(data), status

    def clear_queue(self) -> tuple[Response, int]:
        """
        Clear one or more requests from the queue.

        This endpoint clears a specific request from the queue if a 'uuid' is provided in the JSON payload.
        If no UUID is provided, it clears all requests from the queue.
        It ensures the request contains a valid JSON payload and returns descriptive errors if validations fail.

        Returns:
            tuple[Response, int]: A tuple containing a JSON response that indicates the result of the clear operation,
                                  along with the appropriate HTTP status code.
        """
        logging.debug("clear_queue called to remove a queued request")

        try:
            if not request.is_json:
                logging.warning("Request body is missing or not JSON.")
                return jsonify({"error": "Request body must be JSON"}), 400

            data = request.get_json(silent=True)
            if not data:
                return {"error": "No JSON found in the request"}, 400
            uuid = data.get("uuid")

            if uuid:
                logging.debug("Clearing request with UUID: %s", uuid)
                if self.queue.clear(uuid):
                    logging.info("Successfully removed request with UUID: %s", uuid)
                    return jsonify({"message": f"Successfully removed request with UUID {uuid}"}), 200
                else:
                    logging.warning("UUID %s not found in queue.", uuid)
                    return jsonify({"error": "UUID not found in queue"}), 404
            else:
                if self.queue.clear():
                    logging.info("Successfully cleared all requests.")
                    return jsonify({"message": "Successfully cleared all requests"}), 200

        except Exception as e:
            logging.error("Error clearing requests: %s", e, exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

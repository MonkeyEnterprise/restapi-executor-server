import logging
from functools import wraps
from flask import Flask, request, jsonify

class ApiRoutes:
    
    CONFIG_KEY_REQUEST_QUEUE = "REQUEST_QUEUE"
    CONFIG_KEY_API_KEY = "API_KEY"
    
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.app.config.setdefault(self.CONFIG_KEY_API_KEY, None)
        self.app.config.setdefault(self.CONFIG_KEY_REQUEST_QUEUE, None)
        self.register_routes()

    def require_api_key(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = self.app.config.get(self.CONFIG_KEY_API_KEY)
            if api_key:
                provided_key = request.headers.get("X-API-Key")
                if provided_key != api_key:
                    logging.warning("Unauthorized access attempt.")
                    return jsonify({"error": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return wrapper

    def register_routes(self) -> None:
        self.app.add_url_rule("/", view_func=self.require_api_key(self.status), methods=["GET"])
        self.app.add_url_rule("/queue", view_func=self.require_api_key(self.queue_request), methods=["POST"])
        self.app.add_url_rule("/queue", view_func=self.require_api_key(self.queue_get), methods=["GET"])
        self.app.add_url_rule("/queue/delete", view_func=self.require_api_key(self.queue_clear), methods=["POST"])
        self.register_error_handlers()

    def register_error_handlers(self) -> None:
        @self.app.errorhandler(404)
        def page_not_found(e):
            return jsonify({"error": "Not found"}), 404

    def status(self):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        return jsonify({
            "message": "REST API server online.",
            "client_ip": client_ip
        }), 200

    def queue_request(self):
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "No request data received"}), 400

        queue = self.app.config.get(self.CONFIG_KEY_REQUEST_QUEUE)
        if queue is None:
            return jsonify({"error": "Queue is not configured"}), 500

        response, status_code = queue.add(request_data)
        return jsonify(response), status_code

    def queue_get(self):
        queue = self.app.config.get(self.CONFIG_KEY_REQUEST_QUEUE)
        if queue is None:
            return jsonify({"error": "Queue is not configured"}), 500

        response, status_code = queue.get()
        return jsonify(response), status_code

    def queue_clear(self):
        uuid = request.args.get("uuid")
        if not uuid:
            return jsonify({"error": "UUID parameter is required"}), 400

        queue = self.app.config.get(self.CONFIG_KEY_REQUEST_QUEUE)
        if queue is None:
            return jsonify({"error": "Queue is not configured"}), 500

        if uuid.lower() == "all":
            response, status_code = queue.clear()
        else:
            response, status_code = queue.clear(uuid)
        return jsonify(response), status_code

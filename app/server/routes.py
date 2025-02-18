##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# This module implements a Flask-based REST API server and a thread-safe
# command queue for managing and processing commands.
##


from flask import Flask
from typing import Callable, Any

class Routes:
    """Manages route registrations for a Flask application."""
    
    AVAILABLE_METHODS: set[str] = {"GET", "POST", "DELETE"}

    def __init__(self, app: Flask) -> None:
        """Initializes the Routes class with a reference to a Flask application.

        Args:
            app (Flask): The Flask application instance to which routes will be added.
        """
        self.app = app

    def add(self, endpoint: str, func_name: str, func: Callable[..., Any], method: str) -> None:
        """Registers a new route with the Flask application, ensuring proper type checks.

        Args:
            endpoint (str): The URL route (e.g., "/api/resource").
            func_name (str): The name assigned to the view function.
            func (Callable[..., Any]): The function that handles requests to the route.
            method (str): The HTTP method for the route (e.g., "GET", "POST").

        Raises:
            TypeError: If any of the parameters are not of the expected type.
            ValueError: If the HTTP method is not a valid method.
        """
        if not isinstance(endpoint, str):
            raise TypeError(f"Expected 'endpoint' to be a string, got {type(endpoint).__name__}")
        if not isinstance(func_name, str):
            raise TypeError(f"Expected 'func_name' to be a string, got {type(func_name).__name__}")
        if not callable(func):
            raise TypeError("Expected 'func' to be callable")
        if not isinstance(method, str):
            raise TypeError(f"Expected 'method' to be a string, got {type(method).__name__}")

        method = method.upper()
        if method not in self.AVAILABLE_METHODS:
            raise ValueError(f"Invalid HTTP method: '{method}'. Expected one of {self.AVAILABLE_METHODS}")

        self.app.add_url_rule(endpoint, func_name, func, methods=[method])

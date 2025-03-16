##
#
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
##

from flask import Flask
from typing import Callable, Any

class Routes:
    """
    Manages route registrations for a Flask application.

    This class simplifies the process of adding new URL routes by performing type checks on the provided parameters
    and ensuring that only allowed HTTP methods are used.
    """
    
    AVAILABLE_METHODS: set[str] = {"GET", "POST", "DELETE"}

    def __init__(self, app: Flask) -> None:
        """
        Initialize the Routes instance with a Flask application.

        Args:
            app (Flask): The Flask application instance to which routes will be added.
        """
        self.app = app

    def add(self, endpoint: str, func_name: str, func: Callable[..., Any], method: str) -> None:
        """
        Registers a new route with the Flask application.

        This method adds a new URL rule to the Flask application by associating the given endpoint with a view function.
        It validates the input parameters to ensure they are of the correct types and that the HTTP method is allowed.
        
        Args:
            endpoint (str): The URL route (e.g., "/api/resource") where the view function will be accessible.
            func_name (str): A unique name assigned to the view function.
            func (Callable[..., Any]): The function that handles requests to the specified endpoint.
            method (str): The HTTP method for the route (e.g., "GET", "POST", "DELETE").

        Raises:
            TypeError: If 'endpoint', 'func_name', or 'method' are not strings, or if 'func' is not callable.
            ValueError: If the provided HTTP method is not among the allowed methods: GET, POST, or DELETE.
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

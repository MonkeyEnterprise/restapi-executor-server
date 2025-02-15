import requests
import logging
import traceback
from requests.adapters import HTTPAdapter, Retry

class Session:
    """Manages a persistent requests session with retry logic and exception handling."""

    def __init__(self, url:str, retries: int = 3, ssl: bool = False, timeout = 5):
        """Sets up a persistent requests session with retries."""
        self.timeout = timeout
        self.url = url
        self.online = False
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        protocol = "https://" if ssl else "http://"
        self.session.mount(protocol, HTTPAdapter(max_retries=retry_strategy))


    def __call__(self) -> "Session":
        """Allows the instance to be called like a function, returning the session."""
        return self
    

    def get(self, endpoint: str = ""):
        """Makes a GET request with built-in error handling."""
        url = f"{self.url}/{endpoint}" if endpoint else self.url  # Ensure valid URL

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raise an HTTPError if the status is 4xx or 5xx
            self.online = True
            return response  # Return response object if successful

        except requests.exceptions.Timeout:
            logging.error(f"Timeout while requesting {url}")
        except requests.exceptions.ConnectionError:
            logging.error(f"Connection error - Unable to reach {url}")
        except requests.RequestException as e:
            logging.error(f"Request error for {url}: {e}")
            logging.debug(traceback.format_exc())

        self.online = False
        return None  # Return None on failure
    
    def is_online(self) -> bool:
        return self.is_online()




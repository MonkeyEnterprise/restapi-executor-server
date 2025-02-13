import time
import requests
import logging
import traceback
import json
from requests.adapters import HTTPAdapter, Retry


class CommandExecutor:
    """Handles fetching, executing, and updating commands."""

    def __init__(self):
        """Initializes configuration and session settings."""
        self.server_url = "http://192.168.100.2/api/v1/callsToExecute"
        self.status_update_url = "http://192.168.100.2/api/v1/updateStatus"
        self.propresenter_url = "http://localhost:8000"
        self.polling_interval = 5  # Seconds

        self._setup_logging()
        self.session = self._setup_session()

    def _setup_logging(self):
        """Configures logging settings."""
        logging.basicConfig(
            level=logging.DEBUG,  # Set to DEBUG for extensive logging
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def _setup_session(self):
        """Sets up a persistent requests session with retries."""
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        return session

    def fetch_commands(self):
        """Fetches pending commands from the server."""
        logging.info("Fetching commands from API...")
        try:
            start_time = time.time()
            response = self.session.get(self.server_url, timeout=5)
            response.raise_for_status()  # Raises an error for bad status codes

            elapsed_time = round(time.time() - start_time, 3)
            commands = response.json()

            logging.info(f"Fetched {len(commands)} commands in {elapsed_time}s")
            logging.debug(f"Response Content: {commands}")

            return commands
        except requests.exceptions.Timeout:
            logging.error("Timeout error while fetching commands.")
        except requests.exceptions.ConnectionError:
            logging.error("Connection error - Unable to reach the API server.")
        except requests.RequestException as e:
            logging.error(f"Unexpected error while fetching commands: {e}")
            logging.debug(traceback.format_exc())

        return []

    def send_status_update(self, command, response):
        """Sends the command execution status back to the server."""
        status_payload = {
            "command": command,
            "status_code": response.status_code if response else 500,
            "response": response.text if response else "No response"
        }
        logging.info(f"Sending status update for command {command.get('id', 'unknown')}...")

        try:
            start_time = time.time()
            res = self.session.post(self.status_update_url, json=status_payload, timeout=5)
            elapsed_time = round(time.time() - start_time, 3)

            if res.status_code == 200:
                logging.info(f"Status update successful in {elapsed_time}s")
            else:
                logging.warning(f"Failed to update status: {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            logging.error("Timeout error while sending status update.")
        except requests.exceptions.ConnectionError:
            logging.error("Connection error - Unable to reach the status update server.")
        except requests.RequestException as e:
            logging.error(f"Unexpected error while sending status update: {e}")
            logging.debug(traceback.format_exc())


    def execute_command(self, command):
        """Executes a command by making an HTTP request to ProPresenter."""
        try:
            endpoint = command['endpoint']
            method = command.get("method", "GET").upper()
            data = command.get("data", {})

            logging.info(f"Executing command: {command}")

            if method not in ["POST", "GET"]:
                logging.warning(f"Unsupported method '{method}' in command: {command}")
                return

            start_time = time.time()

            if endpoint == "trigger" and method == "POST":
                # Extract necessary data
                message_id = data.get("messageID")
                message_token = data.get("messageToken")
                message_content = data.get("messageContent")

                if not all([message_id, message_token, message_content]):
                    logging.error("Missing required data fields for triggering message.")
                    return

                # Construct the URL and raw text payload
                url = f"{self.propresenter_url}/message/{message_id}/trigger"
                payload = json.dumps([
                    {
                        "name": message_token,
                        "text": {
                            "text": message_content
                        }
                    }
                ])

                headers = {"Content-Type": "text/plain"}  # Ensure it's sent as raw text

                response = self.session.post(url, data=payload, headers=headers, timeout=5)
            else:
                url = f"{self.propresenter_url}/{endpoint}"
                if method == "POST":
                    response = self.session.post(url, json=data, timeout=5)
                elif method == "GET":
                    response = self.session.get(url, params=data if data else None, timeout=5)

            elapsed_time = round(time.time() - start_time, 3)

            logging.info(f"Executed {method} {url} - Status {response.status_code} in {elapsed_time}s")
            logging.debug(f"Response Content: {response.text}")

            self.send_status_update(command, response)
        except requests.exceptions.Timeout:
            logging.error(f"Timeout while executing command: {command}")
        except requests.exceptions.ConnectionError:
            logging.error(f"Connection error - Unable to reach {self.propresenter_url}")
        except requests.RequestException as e:
            logging.error(f"Error executing command: {e}")
            logging.debug(traceback.format_exc())
            self.send_status_update(command, None)




    def run(self):
        """Main loop to fetch and execute commands continuously."""
        logging.info("Command execution service started. Listening for commands...")

        try:
            while True:
                commands = self.fetch_commands()
                for cmd in commands:
                    self.execute_command(cmd)
                time.sleep(self.polling_interval)
        except KeyboardInterrupt:
            logging.info("Shutting down command execution service.")
        except Exception as e:
            logging.critical(f"Unexpected crash: {e}")
            logging.debug(traceback.format_exc())


if __name__ == "__main__":
    executor = CommandExecutor()
    executor.run()

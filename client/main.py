##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
#
# This module implements a Flask-based REST API server and a thread-safe
# command queue for managing and processing commands.
##

from session import Session
import logging


class ProPresenterClient:
    """Handles fetching, executing, and updating commands."""

    def __init__(self, host: str, port: int, ssl:bool = False)-> None:
        """Initializes configuration and session settings."""        
         # Setup the connection with ProPresenter.
        if (port > 0):
            url = f"{'https://' if ssl else 'http://'}{host}:{port}"
        else:
            url = f"{'https://' if ssl else 'http://'}{host}"

        self.session = Session(url=url, retries=5, ssl=False, timeout=1)()

    def version(self) -> dict:
        """Requests general information about the currently active ProPresenter instance."""        
        response = self.session.get("version")
        return response.json() if response else {}  # Return empty dict if request fails


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    client = ProPresenterClient(host='localhost', port=8000)
    
    pp_info: dict = {}
    while client.session.is_online == True:
        print("Connecting to ProPresenter 7 ...")
        pp_info = client.version()
    
    print(pp_info)
    print("Connected to ProPresenter 7.")





#  def get_args():
#     """
#     Parses command-line arguments for configuring the Flask server.

#     Returns:
#         argparse.Namespace: An object containing parsed arguments.
#     """
#     parser = argparse.ArgumentParser(
#         description="Start the Flask API server.", 
#         add_help=False  # Disable help to avoid conflicts with Gunicorn's arguments.
#     )
#     parser.add_argument("--host", type=str, default=os.environ.get("HOST", "localhost"), help="Host IP address")
#     parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)), help="Port number")
#     parser.add_argument("--polling_interval", type=int, default=int(os.environ.get("POLLING_INTERVAL", 5)), help="Polling interval")
#     args, _ = parser.parse_known_args()  # Ignore any unknown arguments.
#     return args  


    # def fetch_commands(self, timeout: int = 5) -> Any:
    #     """Fetches pending commands from the server."""
    #     logging.info("Fetching commands from API...")
    #     try:
    #         start_time = time.time()
    #         response = self.session.get(f"{self.server_url}/api/v1/callsToExecute", timeout=timeout)
    #         response.raise_for_status()  # Raises an error for bad status codes

    #         elapsed_time = round(time.time() - start_time, 3)
    #         commands = response.json()

    #         logging.info(f"Fetched {len(commands)} commands in {elapsed_time}s")
    #         logging.debug(f"Response Content: {commands}")

    #         return commands
    #     except requests.exceptions.Timeout:
    #         logging.error("Timeout error while fetching commands.")
    #     except requests.exceptions.ConnectionError:
    #         logging.error("Connection error - Unable to reach the API server.")
    #     except requests.RequestException as e:
    #         logging.error(f"Unexpected error while fetching commands: {e}")
    #         logging.debug(traceback.format_exc())

    #     return []

    # def send_status_update(self, command, response, timeout = 5):
    #     """Sends the command execution status back to the server."""
    #     payload = {
    #         "command": command,
    #         "status_code": response.status_code if response else 500,
    #         "response": response.text if response else "No response"
    #     }
    #     logging.info(f"Sending status update for command {command.get('id', 'unknown')}...")

    #     try:
    #         start_time = time.time()
    #         response = self.session.post(f"{self.server_url}/api/v1/updateStatus", json=payload, timeout=timeout)
    #         elapsed_time = round(time.time() - start_time, 3)

    #         if response.status_code == 200:
    #             logging.info(f"Status update successful in {elapsed_time}s")
    #         else:
    #             logging.warning(f"Failed to update status: {response.status_code} - {response.text}")
    #     except requests.exceptions.Timeout:
    #         logging.error("Timeout error while sending status update.")
    #     except requests.exceptions.ConnectionError:
    #         logging.error("Connection error - Unable to reach the status update server.")
    #     except requests.RequestException as e:
    #         logging.error(f"Unexpected error while sending status update: {e}")
    #         logging.debug(traceback.format_exc())


    # def trigger(self, command):
    #     """Executes a command by making an HTTP request to ProPresenter."""
    #     try:
  
    #         data = command.get("data", {})

    #         logging.info(f"Executing command: {command}")

    #         start_time = time.time()
    #         # Extract necessary data
    #         message_id = data.get("messageID")
    #         message_token = data.get("messageToken")
    #         message_content = data.get("messageContent")

    #         if not all([message_id, message_token, message_content]):
    #             logging.error("Missing required data fields for triggering message.")
    #             return

    #         # Construct the URL and raw text payload
    #         url = f"{self.propresenter_url}/v1/message/{message_id}/trigger"
    #         payload = json.dumps([
    #             {
    #                 "name": message_token,
    #                 "text": {
    #                     "text": message_content
    #                 }
    #             }
    #         ])

    #         headers = {"Content-Type": "application/json"}  # Ensure it's sent as raw text
    #         response = self.session.post(url, data=payload, headers=headers, timeout=5)

    #         elapsed_time = round(time.time() - start_time, 3)

    #         logging.info(f"Executed {url} - Status {response.status_code} in {elapsed_time}s")
    #         logging.debug(f"Response Content: {response.text}")

    #         self.send_status_update(command, response)
    #     except requests.exceptions.Timeout:
    #         logging.error(f"Timeout while executing command: {command}")
    #     except requests.exceptions.ConnectionError:
    #         logging.error(f"Connection error - Unable to reach {self.propresenter_url}")
    #     except requests.RequestException as e:
    #         logging.error(f"Error executing command: {e}")
    #         logging.debug(traceback.format_exc())
    #         self.send_status_update(command, None)






    # def run(self):
    #     """Main loop to fetch and execute commands continuously."""
    #     logging.info("Command execution service started. Listening for commands...")

    #     try:
    #         while True:
    #             commands = self.fetch_commands() or []  # Ensure always iterable

    #             for command in commands:
    #                 try:
    #                     if not isinstance(command, dict) or 'endpoint' not in command:
    #                         logging.error(f"Malformed command received: {command}")
    #                         continue  # Skip bad command
    #                     else :
    #                         if command.get("endpoint") == "trigger":
    #                             self.trigger(command)
 
    #                 except Exception as e:
    #                     logging.error(f"Error executing command: {command}")
    #                     logging.debug(traceback.format_exc())

    #             time.sleep(self.polling_interval)

    #     except KeyboardInterrupt:
    #         logging.info("Shutting down command execution service.")
    #     except Exception as e:
    #         logging.critical(f"Unexpected crash: {e}")
    #         logging.debug(traceback.format_exc())



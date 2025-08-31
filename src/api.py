"""
API client for interacting with Balatro game.
"""

import requests
import time
from typing import Iterable


class APIClient:
    """API client for interacting with the Balatro game."""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def start_balatro(self):
        """Start Balatro on the remote desktop."""
        res = requests.post(f"{self.base_url}/start_balatro")
        time.sleep(2)
        if res.status_code != 200:
            print("Error starting Balatro. Check the server logs.")
        else:
            return res.json()

    def stop_balatro(self):
        """Stop Balatro on the remote desktop."""
        res = requests.post(f"{self.base_url}/stop_balatro")
        time.sleep(2)
        if res.status_code != 200:
            print("Error stopping Balatro. Check the server logs.")

    def start_run(self, deck: str = "b_blue", stake: int = 1, controller_type: str = "gamepad"):
        """Start a new run."""
        if controller_type == "gamepad":
            self.send_gamepad_command("RIGHT RIGHT")
        res = requests.post(f"{self.base_url}/auto_start", json={"deck": deck, "stake": stake})
        if res.status_code != 200:
            print("Error starting the run. Check the server logs.")

        return res.json()

    def restart_balatro(self, deck: str = "b_blue", stake: int = 1, controller_type: str = "gamepad"):
        """Fully restart Balatro."""
        self.stop_balatro()
        time.sleep(2)
        self.start_balatro()
        time.sleep(2)
        resp = self.start_run(deck, stake, controller_type=controller_type)
        return resp

    def send_gamepad_command(self, button_sequence: str):
        """Send a gamepad command directly to the API."""
        try:
            payload = {
                "buttons": button_sequence,
                "duration": 0.1
            }

            response = requests.post(
                f"{self.base_url}/gamepad/buttons",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return result
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                return {"status": "error", "message": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return {"status": "error", "message": error_msg}

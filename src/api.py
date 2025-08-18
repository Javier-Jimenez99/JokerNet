"""
API client for interacting with Balatro game.
"""

import requests
import time
from typing import Iterable


class APIClient:
    """Cliente API para interactuar con el juego Balatro."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def start_balatro(self):
        """Iniciar Balatro en el escritorio remoto."""
        res = requests.post(f"{self.base_url}/start_balatro")
        time.sleep(2)
        if res.status_code != 200:
            print("Error al iniciar Balatro. Revisa los logs del servidor.")
        else:
            return res.json()

    def stop_balatro(self):
        """Detener Balatro en el escritorio remoto."""
        res = requests.post(f"{self.base_url}/stop_balatro")
        time.sleep(2)
        if res.status_code != 200:
            print("Error al detener Balatro. Revisa los logs del servidor.")

    def start_run(self, deck:str="b_blue", stake:int=1, controller_type:str="gamepad"):
        """Iniciar nueva run."""
        if controller_type == "gamepad":
            self.send_gamepad_command("RIGHT RIGHT")
        res = requests.post(f"{self.base_url}/auto_start", json={"deck": deck, "stake": stake})
        if res.status_code != 200:
            print("Error al iniciar la run. Revisa los logs del servidor.")

        return res.json()

    def restart_balatro(self, deck:str="b_blue", stake:int=1, controller_type:str="gamepad"):
        """Reiniciar Balatro completamente."""
        self.stop_balatro()
        time.sleep(2)
        self.start_balatro()
        time.sleep(2)
        resp = self.start_run(deck, stake, controller_type=controller_type)
        return resp
    
    def send_gamepad_command(self, button_sequence:str):
        """Enviar comando de gamepad directamente a la API."""
        try:
            # Hacer llamada directa a la API REST
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
            error_msg = f"Error de conexión: {str(e)}"
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return {"status": "error", "message": error_msg}

"""
API client for interacting with Balatro game.
"""

import requests
import time
import streamlit as st


class APIClient:
    """Cliente API para interactuar con el juego Balatro."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def start_balatro(self):
        """Iniciar Balatro en el escritorio remoto."""
        res = requests.post(f"{self.base_url}/start_balatro")
        time.sleep(2)
        if res.status_code != 200:
            st.error("Error al iniciar Balatro. Revisa los logs del servidor.")
    
    def start_run(self, deck="b_blue", stake=1):
        """Iniciar nueva run."""
        st.session_state.game_started = True
        res = requests.post(f"{self.base_url}/auto_start", json={"deck": deck, "stake": stake})
        if res.status_code != 200:
            st.error("Error al iniciar la run. Revisa los logs del servidor.")
    
    def restart_balatro(self):
        """Reiniciar Balatro completamente."""
        requests.post(f"{self.base_url}/stop_balatro")
        time.sleep(2)
        self.start_balatro()
        with st.spinner("Iniciando Balatro…", show_time=True):
            time.sleep(5)
        self.start_run()
    
    def send_gamepad_command(self, button_sequence):
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
                st.success(f"✅ {button_sequence}")
                return result
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                st.error(error_msg)
                return {"status": "error", "message": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión: {str(e)}"
            st.error(error_msg)
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            return {"status": "error", "message": error_msg}

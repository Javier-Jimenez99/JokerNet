"""
Balatro Remote Desktop - Streamlit Application

Aplicación principal simplificada con UI reorganizada.
"""

import streamlit as st
import time

from api import APIClient
from ui_components import (
    render_agent_config,
    render_run_config,
    render_vnc_viewer,
    init_session_state,
    render_chat
)


def main():
    """Función principal de la aplicación."""
    # Configuración de la página
    st.set_page_config(layout="wide", page_title="Balatro - Escritorio Remoto")
    
    # Inicializar estado de la sesión
    init_session_state()
    
    # Instanciar el cliente API
    api_client = APIClient()
    
    # Iniciar Balatro automáticamente
    api_client.start_balatro()

    # Iniciar juego si no está iniciado
    if not st.session_state.get("game_started", False):
        with st.spinner("Iniciando Balatro…", show_time=True):
            time.sleep(5)
        api_client.start_run()

    # Título principal
    st.title("🃏 Balatro - Escritorio Remoto")

    render_agent_config()
    render_run_config(api_client)

    # Layout principal en dos columnas
    left_column, right_column = st.columns(2)
    
    with left_column:   
        # Interfaz de control (Chat + Gamepad)
        render_chat(api_client)

    with right_column:
        # Visor VNC
        render_vnc_viewer()


if __name__ == "__main__":
    main()

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

    # Título principal
    st.title("🃏 Balatro - Escritorio Remoto")

    # Iniciar juego si no está iniciado
    if not st.session_state.game_started:
        with st.spinner("Iniciando Balatro…", show_time=True):
            resp = api_client.restart_balatro(
                deck=st.session_state.deck, 
                stake=st.session_state.stake,
                controller_type=st.session_state.mcp_type
            )
            time.sleep(2)

        if resp.get("status") == "success":
            st.session_state["game_started"] = True
        else:
            st.error("Error al iniciar la run. Revisa los logs del servidor.")

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

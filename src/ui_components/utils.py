import streamlit as st
from .agent import create_agent
from streamlit.components.v1 import html


def init_session_state():
    """Inicializar estado de la sesión."""
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "mcp_type" not in st.session_state:
        st.session_state.mcp_type = "gamepad"
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    if "agent" not in st.session_state:
        with st.spinner("Inicializando agente IA..."):
            try:
                st.session_state.agent = create_agent()
            except Exception as e:
                st.error("Failed to initialize AI agent. Please check your configuration.")
                raise
    if "deck" not in st.session_state:
        st.session_state.deck = "b_blue"
    if "stake" not in st.session_state:
        st.session_state.stake = 1
    if "max_iterations" not in st.session_state:
        st.session_state.max_iterations = 25
    if "max_worker_steps" not in st.session_state:
        st.session_state.max_worker_steps = 3
    if "max_planner_steps" not in st.session_state:
        st.session_state.max_planner_steps = 5

def render_vnc_viewer():
    """Renderizar visor VNC."""
    novnc_url = "http://localhost:6080/vnc.html?autoconnect=1&reconnect=1&resize=scale&view_only=1"
    html(f'<iframe src="{novnc_url}" style="border:none;height:100vh;width:100%" allowfullscreen></iframe>', height=820)
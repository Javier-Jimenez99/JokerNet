
"""
Balatro Remote Desktop - Streamlit Application

Main application with reorganized UI.
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
    """Main application function."""
    # Page configuration
    st.set_page_config(layout="wide", page_title="Balatro - Remote Desktop")

    # Initialize session state
    init_session_state()

    # Instantiate API client
    api_client = APIClient()

    # Main title
    st.title("🃏 Balatro - Remote Desktop")

    # Start game if not started
    if not st.session_state.game_started:
        with st.spinner("Starting Balatro…", show_time=True):
            resp = api_client.restart_balatro(
                deck=st.session_state.deck,
                stake=st.session_state.stake,
                controller_type=st.session_state.mcp_type
            )
            time.sleep(2)

        if resp.get("status") == "success":
            st.session_state["game_started"] = True
        else:
            st.error("Error starting the run. Check the server logs.")

    render_agent_config()
    render_run_config(api_client)

    # Main layout in two columns
    left_column, right_column = st.columns(2)

    with left_column:
        # Control interface (Chat + Gamepad)
        render_chat(api_client)

    with right_column:
        # VNC viewer
        render_vnc_viewer()

if __name__ == "__main__":
    main()

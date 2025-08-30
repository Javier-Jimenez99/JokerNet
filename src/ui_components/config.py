"""
Configuration panel component.
"""

import streamlit as st
import os
from .agent import recreate_agent


def render_agent_config():
    """Render agent configuration panel."""
    with st.expander("⚙️ Agent Configuration", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # Use on_change to automatically apply changes
            old_mcp_type = st.session_state.mcp_type
            mcp_type = st.selectbox(
                "MCP Type:",
                ["gamepad"],
                index=0,
                key="mcp_selector",
                help="Select the type of controller to use. By the moment mouse is disabled"
            )

            if mcp_type != old_mcp_type:
                st.session_state.mcp_type = mcp_type
                st.session_state.game_started = False
                try:
                    recreate_agent()
                except Exception as e:
                    st.error(f"❌ Error recreating agent: {e}")
                    return
                st.success(f"🔄 Changed to mode {mcp_type}")
                st.rerun()

            st.session_state.max_iterations = st.number_input(
                "Max agent iterations", min_value=1, max_value=100, value=st.session_state.max_iterations, step=1
            )

        with col2:
            st.session_state.max_planner_steps = st.number_input(
                "Max planner steps", min_value=1, max_value=20, value=st.session_state.max_planner_steps, step=1
            )

            st.session_state.max_worker_steps = st.number_input(
                "Max worker steps", min_value=1, max_value=20, value=st.session_state.max_worker_steps, step=1
            )

        debug_mode = st.checkbox(
            "🐛 Debug Mode",
            value=st.session_state.debug_mode,
            help="Show messages sent to the model",
            key="debug_checkbox",
            on_change=_on_debug_mode_change
        )

        # Show current status
        debug_status = "🐛 ON" if st.session_state.debug_mode else "🐛 OFF"
        st.info(f"🔮 Agent: **Worker**  |  🎮 MCP: **{st.session_state.mcp_type}**  |  {debug_status}  | 🧠 Model used: **{os.getenv('AZURE_OPENAI_MODEL')}**")




def _on_debug_mode_change():
    """Callback when debug mode changes."""
    new_debug_mode = st.session_state.debug_checkbox
    st.session_state.debug_mode = new_debug_mode
    debug_status = "enabled" if new_debug_mode else "disabled"
    st.success(f"🐛 Debug Mode {debug_status}")
    st.rerun()


def render_run_config(api_client):
    """Render game controls."""

    with st.expander("🎮 Game Configuration", expanded=False):
        if st.button("🔄 Restart Game"):
            with st.spinner("Restarting Balatro…", show_time=True):
                api_client.restart_balatro(
                    deck=st.session_state.deck,
                    stake=st.session_state.stake,
                    controller_type=st.session_state.mcp_type
                )

            st.success("Game restarted.")
        with st.form("start_game_form"):
            st.markdown("**Configure Run**")
            deck_options = {
                "b_blue": "Blue Deck", "b_red": "Red Deck", "b_yellow": "Yellow Deck",
                "b_green": "Green Deck", "b_black": "Black Deck", "b_magic": "Magic Deck",
                "b_nebula": "Nebula Deck", "b_ghost": "Ghost Deck", "b_abandoned": "Abandoned Deck",
                "b_checkered": "Checkered Deck", "b_zodiac": "Zodiac Deck", "b_painted": "Painted Deck",
                "b_anaglyph": "Anaglyph Deck", "b_plasma": "Plasma Deck", "b_erratic": "Erratic Deck"
            }

            list_deck_options = list(deck_options.keys())
            current_deck_index = list_deck_options.index(st.session_state.deck)
            deck = st.selectbox("Deck:", list_deck_options, format_func=lambda x: deck_options[x], index=current_deck_index)
            stake = st.slider("Difficulty:", 1, 8, st.session_state.stake)

            if st.form_submit_button("Start"):
                st.session_state.deck = deck
                st.session_state.stake = stake
                api_client.start_run(deck, stake)
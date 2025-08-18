"""
Configuration panel component.
"""

import streamlit as st
import os
from .agent import recreate_agent

def render_agent_config():
    """Renderizar panel de configuración."""
    with st.expander("⚙️ Configuración de Agente", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Usar on_change para aplicar automáticamente los cambios
            old_mcp_type = st.session_state.mcp_type
            mcp_type = st.selectbox(
                "Tipo de MCP:",
                ["mouse", "gamepad"],
                index=0 if st.session_state.mcp_type == "mouse" else 1,
                key="mcp_selector",
            )

            if mcp_type != old_mcp_type:
                st.session_state.mcp_type = mcp_type
                st.session_state.game_started = False
                try:
                    recreate_agent()
                except Exception as e:
                    st.error(f"❌ Error al recrear el agente: {e}")
                    return
                st.success(f"🔄 Cambiado a modo {mcp_type}")
                st.rerun()            
        
        with col2:
            st.session_state.max_iterations = st.number_input(
                "Max agent iterations", min_value=1, max_value=100, value=st.session_state.max_iterations, step=1
            )

        debug_mode = st.checkbox(
            "🐛 Modo Debug",
            value=st.session_state.debug_mode,
            help="Mostrar mensajes enviados al modelo",
            key="debug_checkbox",
            on_change=_on_debug_mode_change
        )
        
        # Mostrar estado actual
        debug_status = "🐛 ON" if st.session_state.debug_mode else "🐛 OFF"
        st.info(f"🔮 Agente: **Worker**  |  🎮 MCP: **{st.session_state.mcp_type}**  |  {debug_status}  | 🧠 Model used: **{os.getenv('AZURE_OPENAI_MODEL')}**")



def _on_debug_mode_change():
    """Callback cuando cambia el modo debug."""
    new_debug_mode = st.session_state.debug_checkbox
    st.session_state.debug_mode = new_debug_mode
    debug_status = "activado" if new_debug_mode else "desactivado"
    st.success(f"🐛 Modo Debug {debug_status}")
    st.rerun()

def render_run_config(api_client):
    """Renderizar controles del juego."""
    
    with st.expander("🎮 Configuración de Juego", expanded=False):
        if st.button("🔄 Reiniciar Juego"):
            with st.spinner("Reiniciando Balatro…", show_time=True):
                api_client.restart_balatro(
                    deck=st.session_state.deck, 
                    stake=st.session_state.stake, 
                    controller_type=st.session_state.mcp_type
                )

            st.success("Juego reiniciado.")
        with st.form("start_game_form"):
            st.markdown("**Configurar Partida**")
            deck_options = {
                 "b_blue": "Mazo Azul", "b_red": "Mazo Rojo", "b_yellow": "Mazo Amarillo",
                "b_green": "Mazo Verde", "b_black": "Mazo Negro", "b_magic": "Mazo Mágico",
                "b_nebula": "Mazo Nebulosa", "b_ghost": "Mazo Fantasma", "b_abandoned": "Mazo Abandonado",
                "b_checkered": "Mazo A Cuadros", "b_zodiac": "Mazo Zodíaco", "b_painted": "Mazo Pintado",
                "b_anaglyph": "Mazo Anaglifo", "b_plasma": "Mazo Plasma", "b_erratic": "Mazo Errático"
            }

            list_deck_options = list(deck_options.keys())
            current_deck_index = list_deck_options.index(st.session_state.deck)
            deck = st.selectbox("Mazo:", list_deck_options, format_func=lambda x: deck_options[x], index=current_deck_index)
            stake = st.slider("Dificultad:", 1, 8, st.session_state.stake)

            if st.form_submit_button("Iniciar"):
                st.session_state.deck = deck
                st.session_state.stake = stake
                api_client.start_run(deck, stake)
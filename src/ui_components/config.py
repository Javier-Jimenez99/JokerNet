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
            mcp_type = st.selectbox(
                "Tipo de MCP:",
                ["mouse", "gamepad"],
                index=0 if st.session_state.mcp_type == "mouse" else 1,
                key="mcp_selector",
                on_change=_on_mcp_type_change
            )
        
        with col2:
            debug_mode = st.checkbox(
                "🐛 Modo Debug",
                value=st.session_state.debug_mode,
                help="Mostrar mensajes enviados al modelo",
                key="debug_checkbox",
                on_change=_on_debug_mode_change
            )
        
        # Mostrar estado actual
        debug_status = "🐛 ON" if st.session_state.debug_mode else "🐛 OFF"
        st.info(f"🤖 Agente: **Worker** | 🎮 MCP: **{st.session_state.mcp_type}** | {debug_status} | � Model used: **{os.getenv('AZURE_OPENAI_MODEL')}**")


def _on_mcp_type_change():
    """Callback cuando cambia el tipo de MCP."""
    
    new_mcp_type = st.session_state.mcp_selector
    old_mcp_type = st.session_state.mcp_type
    
    if new_mcp_type != old_mcp_type:
        st.session_state.mcp_type = new_mcp_type
        if new_mcp_type != old_mcp_type:
            recreate_agent()
        st.success(f"🔄 Cambiado a modo {new_mcp_type}")
        st.rerun()


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
            api_client.restart_balatro()
            st.success("Juego reiniciado.")
        with st.form("start_game_form"):
            st.markdown("**Configurar Partida**")
            deck_options = {
                "b_red": "Mazo Rojo", "b_blue": "Mazo Azul", "b_yellow": "Mazo Amarillo",
                "b_green": "Mazo Verde", "b_black": "Mazo Negro", "b_magic": "Mazo Mágico",
                "b_nebula": "Mazo Nebulosa", "b_ghost": "Mazo Fantasma", "b_abandoned": "Mazo Abandonado",
                "b_checkered": "Mazo A Cuadros", "b_zodiac": "Mazo Zodíaco", "b_painted": "Mazo Pintado",
                "b_anaglyph": "Mazo Anaglifo", "b_plasma": "Mazo Plasma", "b_erratic": "Mazo Errático"
            }
            
            deck = st.selectbox("Mazo:", list(deck_options.keys()), format_func=lambda x: deck_options[x])
            stake = st.slider("Dificultad:", 1, 8, 1)
            
            if st.form_submit_button("Iniciar"):
                api_client.start_run(deck, stake)
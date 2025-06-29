import streamlit as st
from streamlit.components.v1 import html
import requests
import time 
import asyncio
from agent import BalatroAgent

def start_balatro():
     """Start the Balatro game in a remote desktop environment."""
     res = requests.post("http://localhost:8000/start_balatro")
     time.sleep(2)

     if res.status_code != 200:
          st.error("Failed to start Balatro game. Please check the server logs.")

def start_game(deck="b_blue", stake=1):
     """Start the game when the button is clicked."""
     st.session_state.game_started = True
     res = requests.post("http://localhost:8000/auto_start", json={"deck": deck, "stake": stake})
     if res.status_code != 200:
          st.error("Failed to start the game. Please check the server logs.")

def restart_balatro():
     """Restart the Balatro game in a remote desktop environment."""
     res = requests.post("http://localhost:8000/stop_balatro")
     time.sleep(2)

     if res.status_code != 200:
          st.error("Failed to stop Balatro game. Please check the server logs.")
     
     start_balatro()

     with st.spinner("Iniciando Balatro…", show_time=True):
          time.sleep(5)

     start_game()

@st.cache_resource
def create_agent():
    """Create the agent using asyncio.run to handle async initialization."""
    async def _create_agent():
        return await BalatroAgent.create()
    
    return asyncio.run(_create_agent())

def init_session_state() -> None:
     """Initialize session state with chat history and agent."""
     if "game_started" not in st.session_state:
          st.session_state.game_started = False
     if "chat_history" not in st.session_state:
          st.session_state.chat_history = []
     if "agent" not in st.session_state:
          # Mostrar spinner mientras se crea el agente
          with st.spinner("Inicializando agente IA..."):
               st.session_state.agent = create_agent()

def display_messages() -> None:
    """Render the conversation stored in session_state."""
    for msg in st.session_state.chat_history:
        if msg["role"] == "system":
            # Skip system message in the visible chat transcript.
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

@st.fragment
def chat_block() -> None:
     display_messages()
     user_input = st.chat_input(placeholder="Escribe tu mensaje…")

     if user_input:
          # Add user message to history and show immediately.
          st.session_state.chat_history.append({"role": "user", "content": user_input})
          with st.chat_message("user"):
               st.markdown(user_input)

          # Call LangGraph agent.
          with st.spinner("Pensando…"):
               async def call_agent():
                    return await st.session_state.agent.ainvoke({
                         "messages": st.session_state.chat_history
                    })
               
               response = asyncio.run(call_agent())
               
               assistant_response = response["messages"][-1].content
               st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": assistant_response
               })
               
               with st.chat_message("assistant"):
                    st.markdown(assistant_response)

          # Rerun to keep display in sync
          st.rerun(scope="fragment")

if __name__ == "__main__":
     st.set_page_config(layout="wide", page_title="Balatro - Escritorio Remoto")
     
     # Inicializar el estado de la sesión primero
     init_session_state()
     start_balatro()

     if not st.session_state.get("game_started", False):
          with st.spinner("Iniciando Balatro…", show_time=True):
               time.sleep(5)
          start_game()

     st.title("🃏 Balatro - Escritorio Remoto")

     columns = st.columns(2)
     with columns[0]:
          columns1 = st.columns(2)
          with columns1[0]:
               if st.button("Reiniciar Balatro"):
                    restart_balatro()
                    st.success("Balatro reiniciado exitosamente.")
          with columns1[1]:
               with st.expander("Start New Game", expanded=False):
                    with st.form("start_game_form"):
                         deck = st.selectbox(
                              "Selecciona el mazo:",
                              [
                                        "b_red",       
                                        "b_blue",      
                                        "b_yellow",    
                                        "b_green",     
                                        "b_black",     
                                        "b_magic",     
                                        "b_nebula",    
                                        "b_ghost",     
                                        "b_abandoned", 
                                        "b_checkered", 
                                        "b_zodiac",    
                                        "b_painted",   
                                        "b_anaglyph",  
                                        "b_plasma",    
                                        "b_erratic"    
                              ],
                              index=0,
                              format_func=lambda x: {
                                        "b_red": "Mazo Rojo (predeterminado)",
                                        "b_blue": "Mazo Azul",
                                        "b_yellow": "Mazo Amarillo",
                                        "b_green": "Mazo Verde",
                                        "b_black": "Mazo Negro",
                                        "b_magic": "Mazo Mágico",
                                        "b_nebula": "Mazo Nebulosa",
                                        "b_ghost": "Mazo Fantasma",
                                        "b_abandoned": "Mazo Abandonado",
                                        "b_checkered": "Mazo A Cuadros",
                                        "b_zodiac": "Mazo Zodíaco",
                                        "b_painted": "Mazo Pintado",
                                        "b_anaglyph": "Mazo Anaglifo",
                                        "b_plasma": "Mazo Plasma",
                                        "b_erratic": "Mazo Errático"
                              }.get(x, x)
                         )
                         stake = st.slider("Selecciona la dificultad:", 1, 8, 1)
                         start_button = st.form_submit_button("Iniciar juego")
                         
                         if start_button:
                              start_game(deck, stake)

          # Solo mostrar chat si el agente está inicializado
          if "agent" in st.session_state:
               chat_block()
          else:
               st.info("Inicializando agente IA...")

     with columns[1]:
          st.info("🎮 **Balatro** corriendo en el escritorio remoto…")
          novnc_url = (
               "http://localhost:6080/vnc.html"
               "?autoconnect=1"
               "&reconnect=1"
               "&resize=scale"
               "&view_only=1"
          )
          html(f'<iframe src="{novnc_url}" style="border:none;height:100vh;width:100%" allowfullscreen></iframe>',height=820)

import streamlit as st
from streamlit.components.v1 import html
import requests
import time 
import asyncio
from agents import create_openai_agent, OpenSourceBalatroAgent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from typing import Callable, TypeVar
import inspect

from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from streamlit.delta_generator import DeltaGenerator

from langchain_core.callbacks.base import BaseCallbackHandler
from streamlit.external.langchain import StreamlitCallbackHandler
from langgraph.errors import GraphRecursionError

MAX_ITERATIONS = 10

import base64
import io

class SafeStreamlitCallback (StreamlitCallbackHandler):
     """Callback que detecta imágenes en base64 y las muestra correctamente."""

     # Si usas langgraph, asegúrate de coincidir con la firma correcta:
     # def on_tool_end(self, output: Any, *, **kwargs):
     def on_tool_end(self, output, **kwargs):
          # Es un ToolMessage de LangChain     
          artifacts = output.artifact
          updated_artifacts = []
          for artifact in artifacts:
               # Si es una imagen en base64, la renderizamos
               if artifact.type == "image":
                    if isinstance(artifact.data, str) and self._looks_like_b64(artifact.data):
                         self._render_b64(artifact.data)
                    else:
                         st.error("El artefacto no es una imagen válida en base64.")
               else:
                    updated_artifacts.append(artifact)

          output.artifact = updated_artifacts  # Actualizar los artefactos sin imágenes

          # Fallback: comportamiento original
          super().on_tool_end(output, **kwargs)

     # ---------- helpers ----------
     @staticmethod
     def _looks_like_b64(s: str) -> bool:
          return (
               s.startswith("data:image")
               or (len(s) % 4 == 0 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r" for c in s[:64]))
          )

     def _render_b64(self, data: str):
          # Quita encabezado 'data:image/png;base64,' si existiera
          head, _, body = data.partition(",")
          b = base64.b64decode(body if _ else data)

          # Mostrar en Streamlit sin saturar el log
          with st.expander("Imagen generada", expanded=False):
               st.image(io.BytesIO(b))
          # Si quieres guardar temporalmente:
          # with open("tmp.png", "wb") as f: f.write(b)

def get_streamlit_cb(parent_container: DeltaGenerator) -> BaseCallbackHandler:
    fn_return_type = TypeVar('fn_return_type')
    def add_streamlit_context(fn: Callable[..., fn_return_type]) -> Callable[..., fn_return_type]:
        ctx = get_script_run_ctx()

        def wrapper(*args, **kwargs) -> fn_return_type:
            add_script_run_ctx(ctx=ctx)
            return fn(*args, **kwargs)

        return wrapper

    st_cb = SafeStreamlitCallback(parent_container)

    for method_name, method_func in inspect.getmembers(st_cb, predicate=inspect.ismethod):
        if method_name.startswith('on_'):
            setattr(st_cb, method_name, add_streamlit_context(method_func))
    return st_cb

def start_balatro():
     """Iniciar Balatro en el escritorio remoto."""
     res = requests.post("http://localhost:8000/start_balatro")
     time.sleep(2)
     if res.status_code != 200:
          st.error("Error al iniciar Balatro. Revisa los logs del servidor.")

def start_game(deck="b_blue", stake=1):
     """Iniciar nueva partida."""
     st.session_state.game_started = True
     res = requests.post("http://localhost:8000/auto_start", json={"deck": deck, "stake": stake})
     if res.status_code != 200:
          st.error("Error al iniciar la partida. Revisa los logs del servidor.")

def restart_balatro():
     """Reiniciar Balatro completamente."""
     requests.post("http://localhost:8000/stop_balatro")
     time.sleep(2)
     start_balatro()
     with st.spinner("Iniciando Balatro…", show_time=True):
          time.sleep(5)
     start_game()

@st.cache_resource
def create_agent():
     """Crear agente según la configuración seleccionada."""
     agent_type = st.session_state.get("agent_type", "OpenAI")
     mcp_type = st.session_state.get("mcp_type", "mouse")
     
     async def _create():
          if agent_type == "OpenAI":
               agent, tools = await create_openai_agent(server_name=mcp_type)
               return agent
          else:
               return await OpenSourceBalatroAgent.create(server_name=mcp_type)
     
     return asyncio.run(_create())

def recreate_agent():
     """Recrear agente cuando cambia la configuración."""
     create_agent.clear()
     with st.spinner("Reconfigurando agente IA..."):
          st.session_state.agent = create_agent()
     st.session_state.chat_history = []

def init_session_state() -> None:
     """Inicializar estado de la sesión."""
     if "game_started" not in st.session_state:
          st.session_state.game_started = False
     if "chat_history" not in st.session_state:
          st.session_state.chat_history = []
     if "agent_type" not in st.session_state:
          st.session_state.agent_type = "OpenAI"
     if "mcp_type" not in st.session_state:
          st.session_state.mcp_type = "mouse"
     if "agent" not in st.session_state:
          with st.spinner("Inicializando agente IA..."):
               st.session_state.agent = create_agent()

def display_messages() -> None:
     """Mostrar el historial de conversación."""
     for msg in st.session_state.chat_history:
          if msg["role"] != "system":
               with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

@st.fragment
def chat_block() -> None:
     # Contenedor con altura fija para el chat
     with st.container(height=700):  # Reducido un poco para dar espacio al input
          display_messages()

          tools_execution = st.empty()

          # Input del usuario al final
          if user_input := st.chat_input(placeholder="Escribe tu mensaje…"):
               # Añadir mensaje del usuario
               history = st.session_state.get("chat_history", [])
               history.append({"role": "user", "content": user_input})
               st.session_state.chat_history = history

               with st.chat_message("user"):
                    st.write(user_input)

               # Llamar al agente con callback para mostrar herramientas
               with st.chat_message("assistant"):
                    config = {
                         "recursion_limit": MAX_ITERATIONS,  # Máximo de iteraciones
                         "configurable": {"max_iterations": MAX_ITERATIONS},
                         "callbacks": [get_streamlit_cb(tools_execution)]
                    }
                    
                    # Llamar al agente
                    response = asyncio.run(
                         st.session_state.agent.ainvoke(
                              input={
                                   "messages": history
                              },
                              config=config
                         )
                    )

                    last_msg = response["messages"][-1].content
                    st.session_state.chat_history.append({"role": "assistant", "content": last_msg})

                    # Debug: mostrar la estructura de la respuesta
                    #msg_placeholder.write(last_msg)

               # Rerun para mostrar el nuevo mensaje
               st.rerun(scope="fragment")

if __name__ == "__main__":
     st.set_page_config(layout="wide", page_title="Balatro - Escritorio Remoto")
     
     # Inicializar
     init_session_state()
     start_balatro()

     # Iniciar juego si no está iniciado
     if not st.session_state.get("game_started", False):
          with st.spinner("Iniciando Balatro…", show_time=True):
               time.sleep(5)
          start_game()

     st.title("🃏 Balatro - Escritorio Remoto")

     # Configuración del Agente
     with st.expander("⚙️ Configuración del Agente", expanded=False):
          col1, col2 = st.columns(2)
          
          with col1:
               agent_type = st.selectbox(
                    "Tipo de Agente:",
                    ["OpenAI", "OpenSource"],
                    index=0 if st.session_state.agent_type == "OpenAI" else 1
               )
          
          with col2:
               mcp_type = st.selectbox(
                    "Tipo de MCP:",
                    ["mouse", "gamepad"],
                    index=0 if st.session_state.mcp_type == "mouse" else 1
               )
          
          # Aplicar cambios si es necesario
          if agent_type != st.session_state.agent_type or mcp_type != st.session_state.mcp_type:
               if st.button("🔄 Aplicar Configuración", type="primary"):
                    st.session_state.agent_type = agent_type
                    st.session_state.mcp_type = mcp_type
                    recreate_agent()
                    st.success("¡Configuración aplicada!")
                    st.rerun()
          else:
               st.info(f"🤖 Agente: **{st.session_state.agent_type}** | 🎮 MCP: **{st.session_state.mcp_type}**")

     columns = st.columns(2)
     with columns[0]:
          # Controles del juego
          col1, col2 = st.columns(2)
          with col1:
               if st.button("🔄 Reiniciar Balatro"):
                    restart_balatro()
                    st.success("Balatro reiniciado.")
          
          with col2:
               with st.expander("🎮 Nueva Partida", expanded=False):
                    with st.form("start_game_form"):
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
                              start_game(deck, stake)

          # Chat
          if "agent" in st.session_state:
               chat_block()
          else:
               st.info("Inicializando agente IA...")

     with columns[1]:
          st.info("🎮 **Balatro** - Escritorio Remoto")
          novnc_url = "http://localhost:6080/vnc.html?autoconnect=1&reconnect=1&resize=scale&view_only=1"
          html(f'<iframe src="{novnc_url}" style="border:none;height:100vh;width:100%" allowfullscreen></iframe>', height=820)

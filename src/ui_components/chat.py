"""
Chat component for AI interaction.
"""

import streamlit as st
import asyncio
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from streamlit.delta_generator import DeltaGenerator
from langchain_core.callbacks.base import BaseCallbackHandler
from typing import Callable, TypeVar
import inspect
import json
import base64
import io

from .gamepad_controller import render_gamepad_controller
from .agent import format_worker_result_for_chat

MAX_ITERATIONS = 25
# MAX_ITERATIONS = 25  # Removed in favor of configurable value

# Set up a sidebar input for max iterations (default 25)
if "max_iterations" not in st.session_state:
    st.session_state.max_iterations = 25
st.session_state.max_iterations = st.sidebar.number_input(
    "Max agent iterations", min_value=1, max_value=100, value=st.session_state.max_iterations, step=1
)

def display_messages():
    """Mostrar el historial de conversación."""
    for msg in st.session_state.chat_history:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


@st.fragment
def render_chat_block():
    """Renderizar bloque de chat."""
    # Contenedor con altura fija para el chat (solo para mensajes)
    main_container = st.container(height=650)
    with main_container:
        display_messages()
    
    # Input del usuario fuera del contenedor de mensajes
    if user_input := st.chat_input(placeholder="Describe la tarea que quieres que realice..."):
        # Añadir mensaje del usuario al historial
        history = st.session_state.get("chat_history", [])
        history.append({"role": "user", "content": user_input})
        st.session_state.chat_history = history

        with main_container:
            st.chat_message("user").markdown(user_input)
            
            with st.chat_message("assistant"):
                config = {
                    "recursion_limit": MAX_ITERATIONS,
                    "configurable": {"max_iterations": MAX_ITERATIONS},
                    "callbacks": [get_streamlit_cb(st.empty(), debug_mode=st.session_state.debug_mode)]
                }
                
                try:
                    # Usar el Worker con su entrada por defecto
                    response = asyncio.run(
                        st.session_state.agent.ainvoke(
                            input={
                                "task": user_input,
                                "history_messages": [],
                                "screen_descriptions": [],
                                "consecutive_duplicates": 0,
                                "recursion_count": 0,
                                "max_recursions": MAX_ITERATIONS,
                                "history_limit": 20,
                                "done": False
                            },
                            config=config
                        )
                    )
                    
                    # Obtener el resultado del worker
                    if "result" in response and response["result"]:
                        result = response["result"]
                        # Usar la función de formateo para el chat
                        last_msg = format_worker_result_for_chat(result)
                    else:
                        last_msg = "No se pudo obtener un resultado del worker."

                    st.markdown(last_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": last_msg})
                    
                except Exception as e:
                    logging.error("Exception occurred in render_chat_block", exc_info=True)
                    error_msg = f"Error al procesar la solicitud ({type(e).__name__}): {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})


def render_chat_interface():
    """Renderizar interfaz de chat con información contextual."""
    if "agent" not in st.session_state:
        st.info("Inicializando agente IA...")
        return
    
    # Renderizar chat
    render_chat_block()

class CustomToolCallbackHandler(BaseCallbackHandler):
    """Callback personalizado para mostrar llamadas de tools."""

    def __init__(self, parent_container, debug_mode=False):
        self.parent_container = parent_container
        self.debug_mode = debug_mode
        self.current_tool_expander = None
        self.tool_counter = 0

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Se ejecuta cuando comienza la ejecución de una tool."""
        self.tool_counter += 1
        tool_name = serialized.get('name', 'Tool desconocida')
        
        self.current_tool_expander = self.parent_container.expander(
            f"🔧 Tool #{self.tool_counter}: {tool_name}", 
            expanded=True
        )
        
        with self.current_tool_expander:
            st.write("**📥 Entrada:**")
            if isinstance(input_str, str) and len(input_str) > 500:
                with st.expander("Ver entrada completa", expanded=False):
                    st.code(input_str)
            else:
                st.code(str(input_str))
    
    def on_tool_end(self, output, **kwargs):
        """Se ejecuta cuando termina la ejecución de una tool."""
        if self.current_tool_expander is None:
            return
        
        with self.current_tool_expander:
            st.write("**📤 Salida:**")
            
            if hasattr(output, 'artifact') and output.artifact:
                for artifact in output.artifact:
                    if artifact.type == "image":
                        if isinstance(artifact.data, str) and self._looks_like_b64(artifact.data):
                            st.write("🖼️ **Imagen generada:**")
                            self._render_b64(artifact.data)
                        else:
                            st.error("El artefacto no es una imagen válida en base64.")
                    else:
                        st.write(f"📄 **Artifact ({artifact.type}):**")
                        st.code(str(artifact.data))
                        
                if hasattr(output, 'content') and output.content:
                    st.write("**💬 Contenido:**")
                    st.code(output.content)
            else:
                output_str = str(output)
                if len(output_str) > 1000:
                    with st.expander("Ver salida completa", expanded=False):
                        st.code(output_str)
                else:
                    st.code(output_str)
    
    def on_tool_error(self, error, **kwargs):
        """Se ejecuta cuando hay un error en la tool."""
        if self.current_tool_expander is None:
            return
            
        with self.current_tool_expander:
            st.write("**❌ Error:**")
            st.error(str(error))
    
    @staticmethod
    def _looks_like_b64(s: str) -> bool:
        """Verifica si una string parece ser base64."""
        return (
            s.startswith("data:image")
            or (len(s) % 4 == 0 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r" for c in s[:64]))
        )

    def _render_b64(self, data: str):
        """Renderiza una imagen en base64."""
        try:
            head, _, body = data.partition(",")
            b = base64.b64decode(body if _ else data)
            st.image(io.BytesIO(b), caption="Captura de pantalla", use_container_width=True)
        except Exception as e:
            st.error(f"Error al mostrar la imagen: {str(e)}")

    def on_chat_model_start(self, serialized, messages, **kwargs):
        """Mostrar mensajes enviados al modelo si debug mode está activado."""
        if not self.debug_mode:
            return
            
        batch = messages[0] if messages and len(messages) > 0 else []
        snapshot = []
        
        for m in batch:
            if isinstance(m.content, list):
                parts = []
                for p in m.content:
                    if isinstance(p, dict) and p.get("type") in ("image_url", "input_image", "image"):
                        preview = (p.get("image_url", {}).get("url") or "")[:80]
                        parts.append({"type": p["type"], "preview": preview + "..."})
                    else:
                        parts.append({"type": p.get("type", "text"), "text": str(p.get("text", ""))[:160]})
                snapshot.append({"role": m.type, "content": parts})
            else:
                snapshot.append({"role": m.type, "text": str(m.content)[:400]})

        with self.parent_container.expander("📤 Mensajes enviados al modelo", expanded=False):
            st.code(json.dumps(snapshot, ensure_ascii=False, indent=2))


def get_streamlit_cb(parent_container: DeltaGenerator, debug_mode: bool = False) -> BaseCallbackHandler:
    """Crear callback handler con contexto de Streamlit."""
    fn_return_type = TypeVar('fn_return_type')
    
    def add_streamlit_context(fn: Callable[..., fn_return_type]) -> Callable[..., fn_return_type]:
        ctx = get_script_run_ctx()

        def wrapper(*args, **kwargs) -> fn_return_type:
            add_script_run_ctx(ctx=ctx)
            return fn(*args, **kwargs)

        return wrapper

    st_cb = CustomToolCallbackHandler(parent_container, debug_mode=debug_mode)

    for method_name, method_func in inspect.getmembers(st_cb, predicate=inspect.ismethod):
        if method_name.startswith('on_'):
            setattr(st_cb, method_name, add_streamlit_context(method_func))
    return st_cb


def render_chat(api_client):
    """Renderizar tabs de control (Chat y Controles Manuales)."""
    if "agent" not in st.session_state:
        st.info("Inicializando agente IA...")
        return
    
    # Información contextual
    control_info = (
        "🎮 **Gamepad Mode**: Describe una tarea específica que quieres que el agente realice usando controles de gamepad (ej: 'Navega al menú principal', 'Selecciona una carta', 'Ve a configuración')" 
        if st.session_state.mcp_type == "gamepad" 
        else "🖱️ **Mouse Mode**: Describe una tarea específica que quieres que el agente realice usando el mouse (ej: 'Haz clic en el botón Start', 'Selecciona la carta azul', 'Ve al menú de configuración')"
    )
    
    # Crear tabs para Chat y Controles
    chat_tab, controls_tab = st.tabs(["💬 Chat IA", "🎮 Gamepad Controllers"])
    
    with chat_tab:
        render_chat_interface()
    
    with controls_tab:
        render_gamepad_controller(api_client)
import streamlit as st
import asyncio
from agents import create_worker


@st.cache_resource
def create_agent():
    """Crear agente Worker."""
    mcp_type = st.session_state.get("mcp_type", "gamepad")
    
    async def _create():
        worker = await create_worker(server_name=mcp_type)
        return worker
    
    return asyncio.run(_create())


def recreate_agent():
    """Recrear agente cuando cambia la configuración."""
    create_agent.clear()
    with st.spinner("Reconfigurando agente IA..."):
        st.session_state.agent = create_agent()
    st.session_state.chat_history = []

def format_worker_result_for_chat(result):
    """Formatear el resultado del worker para mostrar en el chat."""
    if not result:
        return "No se pudo obtener un resultado del worker."
    
    success = result.get("success", False)
    reason = result.get("reason", "unknown")
    iterations = result.get("iterations", 0)
    description = result.get("description", "")
    
    if success:
        chat_message = f"✅ Tarea completada: {reason}\n\n{description}"
    else:
        chat_message = f"❌ Tarea fallida: {reason}\n\n{description}"
    
    chat_message += f"\n\n📊 Iteraciones: {iterations}"
    
    if "worker_reasoning" in result:
        chat_message += f"\n\n🧠 Razonamiento: {result['worker_reasoning']}"
    
    return chat_message
from typing import Annotated, TypedDict, List, Optional, Iterable
from typing_extensions import Literal
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, ToolMessage, messages_from_dict
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI
from .utils import load_agent_prompt, load_summary_prompt
from dotenv import load_dotenv
from functools import partial

import os
from langgraph.prebuilt import ToolNode
import json

load_dotenv()

class AgentState(TypedDict):
    """
    Estado del agente, diseñado para no acumular mensajes y ser más eficiente.
    """
    initial_task: Iterable[Optional[HumanMessage]]
    last_screenshot: Optional[HumanMessage]
    ai_message: Optional[AIMessage]
    last_ai_with_tools: Optional[AIMessage]  # Para mantener el mensaje AI con tool_calls
    last_tool_message: List[ToolMessage]
    messages: List[AnyMessage]
    recursion_count: int  # Contador de recursiones para límite de parada

def prepare_initial_state_node(state: AgentState) -> dict:
    """
    Toma el primer mensaje del usuario de la lista 'messages'
    y lo establece como la 'initial_task', asegurando que sea un objeto BaseMessage.
    También inicializa el contador de recursión.
    """
    if not state.get("messages"):
        return {"recursion_count": 0}
    
    # Convertir mensajes de formato OpenAI a objetos BaseMessage
    converted_messages = []
    for msg in state["messages"]:
        if isinstance(msg, dict):
            # Si es un diccionario, convertir de formato OpenAI a BaseMessage
            if msg.get("role") == "user":
                converted_messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                converted_messages.append(AIMessage(content=msg["content"]))
            elif msg.get("role") == "system":
                # Los mensajes del sistema generalmente se manejan en el prompt
                pass
        else:
            # Si ya es un objeto BaseMessage, usarlo directamente
            converted_messages.append(msg)
    
    return {
        "initial_task": converted_messages,
        "recursion_count": 0
    }

async def capture_screenshot_node(state: AgentState, screenshot_tool: Runnable) -> dict:
    """Toma una captura de pantalla y la guarda en 'last_screenshot'. También incrementa el contador de recursión."""
    try:
        result = json.loads(await screenshot_tool.ainvoke({}))
        image_data = result.get("screenshot", "")
        mouse_info = result.get("mouse_info", "")

        human_msg = HumanMessage(content=[
            {"type": "text", "text": f"{mouse_info} Current game state:"},
            {"type": "image_url", "image_url": {"url": image_data}}
        ])
        
        # Incrementar el contador de recursión
        current_count = state.get("recursion_count", 0)
        return {
            "last_screenshot": human_msg,
            "recursion_count": current_count + 1
        }
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        human_msg = HumanMessage(content=[
            {"type": "text", "text": f"Screenshot capturing error"},
        ])
        current_count = state.get("recursion_count", 0)
        return {
            "last_screenshot": human_msg,
            "recursion_count": current_count + 1
        }

async def agent_node(state: AgentState, llm: Runnable) -> dict:
    """
    Prepara los mensajes y llama al LLM. Guarda la respuesta en 'ai_message'.
    """
    # Construye la lista de mensajes para el LLM a partir del estado actual
    messages_for_llm = []
    messages_for_llm.extend(state["initial_task"])
    
    # Si hay resultados de herramientas, incluir el mensaje AI anterior con tool_calls
    if state.get("last_tool_message") and state.get("last_ai_with_tools"):
        messages_for_llm.append(state["last_ai_with_tools"])
        messages_for_llm.extend(state["last_tool_message"])

    messages_for_llm.append(state["last_screenshot"])
    
    resp: AIMessage = await llm.ainvoke({"messages": messages_for_llm})
    return {"ai_message": resp}

async def summary_node(state: AgentState, llm: Runnable) -> dict:
    """
    Nodo de resumen que se ejecuta cuando se alcanza el límite de recursión.
    Proporciona un resumen del estado actual y cierra de forma correcta.
    """
    
    # Preparar mensajes para el resumen
    messages_for_summary = []
    messages_for_summary.extend(state["initial_task"])
    if state.get("last_screenshot"):
        messages_for_summary.append(state["last_screenshot"])

    resp: AIMessage = await llm.ainvoke({"messages": messages_for_summary})
    return {"ai_message": resp}

def should_continue(state: AgentState, max_recursions: int = 10) -> Literal["tools", "summary", "__end__"]:
    """Decide si continuar con herramientas, hacer un resumen o finalizar."""
    # Verificar límite de recursión primero
    current_count = state.get("recursion_count", 0)
    if current_count >= max_recursions:
        return "summary"
    
    ai_msg = state.get("ai_message")
    if ai_msg and ai_msg.tool_calls:
        return "tools"
    return END

async def unified_tool_node(state: AgentState, tool_node: Runnable) -> dict:
    """
    Unifica la preparación, ejecución y procesamiento de herramientas en un solo paso.
    Se asegura de que el resultado siempre sea una lista de ToolMessage.
    Guarda también el mensaje AI con tool_calls para mantener el contexto.
    """
    ai_msg = state.get("ai_message")
    if not ai_msg or not ai_msg.tool_calls:
        return {}

    tool_messages = await tool_node.ainvoke([ai_msg])
    
    if not isinstance(tool_messages, list):
        tool_messages = [tool_messages]
    
    return {
        "last_tool_message": tool_messages,
        "last_ai_with_tools": ai_msg  # Guardar el mensaje AI con tool_calls
    }

async def create_openai_agent(server_name: str = "mouse", max_recursions: int = 10) -> Runnable:
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    openai_model = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1")

    assert (
        azure_endpoint and openai_api_key and openai_api_version
    ), "Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_API_VERSION in your environment variables."

    prompt = ChatPromptTemplate.from_messages([
        ("system", load_agent_prompt(control_type=server_name)),
        ("placeholder", "{messages}")
    ])

    client = MultiServerMCPClient(
        {
            "mouse": {"transport": "streamable_http", "url": "http://localhost:8001/mouse/mcp"},
            "gamepad": {"transport": "streamable_http", "url": "http://localhost:8001/gamepad/mcp"}
        }
    )

    tools = await client.get_tools(server_name=server_name)
    
    screenshot_tool = None
    regular_tools = []
    for t in tools:
        tool_name = getattr(t, "name", None)
        if (tool_name == "get_screen_with_cursor" and server_name == "mouse") or \
           (tool_name == "get_screen" and server_name == "gamepad"):
            screenshot_tool = t
        else:
            regular_tools.append(t)

    llm = AzureChatOpenAI(
        azure_deployment=openai_model,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        temperature=0,
    ).bind_tools(regular_tools)

    llm_with_prompt: Runnable = prompt | llm

    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", load_summary_prompt()),
        ("placeholder", "{messages}")
    ])
    
    # LLM sin herramientas para el nodo de resumen
    llm_for_summary = AzureChatOpenAI(
        azure_deployment=openai_model,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        temperature=0,
    )
    llm_summary_with_prompt: Runnable = summary_prompt | llm_for_summary
    
    # Instancia del ToolNode que usaremos en nuestro nodo unificado
    tool_node_runnable = ToolNode(tools=regular_tools)

    # --- Graph Definition ---
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("prepare_initial_state", prepare_initial_state_node)
    graph.add_node("capture_screen", partial(capture_screenshot_node, screenshot_tool=screenshot_tool))
    graph.add_node("agent", partial(agent_node, llm=llm_with_prompt))
    graph.add_node("summary", partial(summary_node, llm=llm_summary_with_prompt))
    graph.add_node("tools", partial(unified_tool_node, tool_node=tool_node_runnable))

    # Define edges
    graph.add_edge(START, "prepare_initial_state")
    graph.add_edge("prepare_initial_state", "capture_screen")
    graph.add_edge("capture_screen", "agent")
    
    # Crear la función should_continue con el límite configurado
    should_continue_with_limit = partial(should_continue, max_recursions=max_recursions)
    
    graph.add_conditional_edges("agent", should_continue_with_limit, {
        "tools": "tools",
        "summary": "summary",
        END: END
    })
    graph.add_edge("tools", "capture_screen")
    graph.add_edge("summary", END)

    compiled_graph = graph.compile()
    return compiled_graph

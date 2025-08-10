from typing import Annotated, TypedDict, List, Dict
from typing_extensions import Literal
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from .utils import load_agent_prompt, create_hermes_system_message
from dotenv import load_dotenv
import os

# Configuration for the compactor
MAX_TURNS = 12  # last N entries (adjustable)


class AgentState(TypedDict):
    # This will allow to add messages dynamically
    messages: Annotated[List[AnyMessage], add_messages]

async def capture_screenshot_node(state: AgentState, screenshot_tool) -> dict:
    """Toma una captura de pantalla automáticamente antes de cada llamada al LLM"""
    try:
        # Ejecutar la herramienta de screenshot
        result = await screenshot_tool.ainvoke({})
        
        # Extraer la imagen del primer artifact (siempre hay uno y siempre es una imagen)
        artifact = result.artifact[0]
        image_data = artifact.data
        
        # Añadir prefijo data:image si no lo tiene
        if not image_data.startswith("data:image"):
            image_data = f"data:image/png;base64,{image_data}"
        
        # Crear mensaje con la imagen actual
        human_msg = HumanMessage(content=[
            {"type": "text", "text": "Current screen:"},
            {
                "type": "image_url", 
                "image_url": {
                    "url": image_data,
                    "detail": "low"  # Para reducir costos de vision
                }
            }
        ])
        return {"messages": [human_msg]}
        
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return {}

def compact_messages_node(state: AgentState) -> dict:
    """
    Compacts messages to avoid consuming too many tokens.
    Removes old ToolMessages and AIMessages that only contain tool_calls.
    Keeps only the most recent image.
    """
    msgs = state.get("messages", [])
    
    # Take only the last MAX_TURNS messages
    msgs = msgs[-MAX_TURNS:] if len(msgs) > MAX_TURNS else msgs
    
    # Find the last "Current screen:" message (our automatic screenshot)
    last_screen_idx = None
    for i in range(len(msgs)-1, -1, -1):
        m = msgs[i]
        if (isinstance(m, HumanMessage) and 
            isinstance(m.content, list) and 
            len(m.content) > 0 and
            isinstance(m.content[0], dict) and
            m.content[0].get("text") == "Current screen:"):
            last_screen_idx = i
            break

    prepared = []
    for i, m in enumerate(msgs):
        # Skip ToolMessages - no longer needed since we don't promote from them
        if isinstance(m, ToolMessage):
            continue

        # If it's an AIMessage with only tool_calls (no text), omit it
        if isinstance(m, AIMessage):
            has_text = isinstance(m.content, str) and m.content.strip()
            has_blocks = isinstance(m.content, list) and len(m.content) > 0
            if not has_text and not has_blocks:
                # Only tool_calls → remove
                continue
            # If it has text AND tool_calls, remove tool_calls but keep the text
            if getattr(m, "tool_calls", None):
                m = AIMessage(content=(m.content if has_text or has_blocks else ""))

        # Remove old "Current screen:" messages; keep only the most recent one
        if (isinstance(m, HumanMessage) and 
            isinstance(m.content, list) and 
            len(m.content) > 0 and
            isinstance(m.content[0], dict) and
            m.content[0].get("text") == "Current screen:"):
            if i == last_screen_idx:
                # Keep the most recent screenshot
                prepared.append(m)
            # Skip older screenshots
            continue

        prepared.append(m)

    return {"messages": prepared}

async def agent_node(state: AgentState, llm: Runnable) -> dict:
    resp: AIMessage = await llm.ainvoke({"messages": state["messages"]})
    return {"messages": [resp]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


class OpenSourceBalatroAgent:
    def __init__(self):
        """Initialize the agent synchronously. Use create() for full setup."""
        self.agent = None
        self.max_iterations = 20

    @classmethod
    async def create(
        cls,
        model: str = "unsloth/Qwen2.5-VL-7B-Instruct-bnb-4bit",
        server_name: str = "mouse",
        max_iterations: int = 10
    ):
        """Create and fully initialize a BalatroAgent instance."""
        instance = cls()
        instance.max_iterations = max_iterations
        await instance._initialize(model, server_name)
        return instance

    async def _initialize(
        self, 
        model: str, 
        server_name: str
    ):
        """Internal async initialization method."""
        load_dotenv()

        llm = ChatOpenAI(
            base_url="http://localhost:8000/v1",
            model_name=model,
            openai_api_key="EMPTY",
            temperature=0,
        )

        client = MultiServerMCPClient({
            "mouse": {
                "transport": "streamable_http",
                "url": "http://localhost:8001/mouse/mcp"
            },
            "gamepad": {
                "transport": "streamable_http",
                "url": "http://localhost:8001/gamepad/mcp"
            }
        })

        tools = await client.get_tools(server_name=server_name)
        
        # Separate screenshot tool from regular tools
        screenshot_tool = None
        regular_tools = []
        
        for t in tools:
            tool_name = getattr(t, "name", None)
            if (tool_name == "get_screen_with_cursor" and server_name == "mouse") or (tool_name == "get_screen" and server_name == "gamepad"):
                screenshot_tool = t
            else:
                regular_tools.append(t)

        # Create system message with regular tools only
        system_contents = create_hermes_system_message(regular_tools)
        system_contents.append({"type": "text", "text": load_agent_prompt(control_type=server_name)})

        # LLM only gets the regular tools (no screenshot tool)
        llm = llm.bind_tools(regular_tools)

        async def agent_wrapper(state: AgentState) -> dict:
            # Add system message if it's the first interaction
            messages = state["messages"]
            if not any(isinstance(m, SystemMessage) for m in messages):
                system_msg = SystemMessage(content=system_contents)
                messages = [system_msg] + messages
            return await agent_node(AgentState(messages=messages), llm)
        
        async def screenshot_wrapper(state: AgentState) -> dict:
            return await capture_screenshot_node(state, screenshot_tool)
        
        agent_node_lambda = RunnableLambda(agent_wrapper).with_config({"run_name": "agent_node"})
        screenshot_node_lambda = RunnableLambda(screenshot_wrapper).with_config({"run_name": "screenshot_node"})
        tools_node = ToolNode(tools=regular_tools)

        graph = StateGraph(AgentState)
        graph.add_node("capture_screen", screenshot_node_lambda)
        graph.add_node("compact_messages", compact_messages_node)
        graph.add_node("agent", agent_node_lambda)
        graph.add_node("tools", tools_node)

        # Simplified flow: START -> capture_screen -> compact -> agent -> tools -> capture_screen -> compact -> agent...
        graph.add_edge(START, "capture_screen")
        graph.add_edge("capture_screen", "compact_messages")
        graph.add_edge("compact_messages", "agent")
        graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
        graph.add_edge("tools", "capture_screen")  # After tools, capture screen again

        self.agent = graph.compile()

    async def ainvoke(self, messages) -> Dict:
        """Invoke the agent with a message and return the response."""
        if self.agent is None:
            raise RuntimeError(
                "Agent not initialized. Use BalatroAgent.create() instead of BalatroAgent()"
            )

        # Convert input to AgentState format
        if isinstance(messages, dict) and "messages" in messages:
            state = messages
        else:
            state = {"messages": messages if isinstance(messages, list) else [messages]}

        # ✅ CONFIGURAR: Límite de recursión/iteraciones
        return await self.agent.ainvoke(
            state,
            config={
                "recursion_limit": self.max_iterations,  # Máximo de iteraciones
                "configurable": {"max_iterations": self.max_iterations},
            },
        )

from typing import Annotated, TypedDict, List
from typing_extensions import Literal
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from .utils import load_agent_prompt
from dotenv import load_dotenv
import os
from langgraph.prebuilt import ToolNode

load_dotenv()


class AgentState(TypedDict):
    # This will allow to add messages dynamically
    messages: Annotated[List[AnyMessage], add_messages]

def to_image_block(url_or_b64: str) -> dict:
    return {"type": "image_url", "image_url": {"url": url_or_b64}}

def extract_image_blocks_from_artifact(tool_message) -> list:
    blocks = []
    
    # Check if the message has artifact
    if hasattr(tool_message, 'artifact') and tool_message.artifact:
        for artifact in tool_message.artifact:
            # If it's a base64 image, convert it to image block
            if artifact.type == "image":
                if hasattr(artifact, 'data') and isinstance(artifact.data, str):
                    # Add data:image prefix if it doesn't have it
                    if artifact.data.startswith("data:image"):
                        blocks.append(to_image_block(artifact.data))
                    elif artifact.data:  # It's base64 without prefix
                        # Assume PNG by default
                        data_url = f"data:image/png;base64,{artifact.data}"
                        blocks.append(to_image_block(data_url))
    
    return blocks

def promote_images_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_msg = messages[-1]
    image_blocks = []

    if isinstance(last_msg, ToolMessage):
        image_blocks = extract_image_blocks_from_artifact(last_msg)

    if image_blocks:
        human_msg = HumanMessage(content=[
            {"type": "text", "text": "Image from tool:"},
            *image_blocks
        ])
        return {"messages": [human_msg]}
    return {}

async def agent_node(state: AgentState, llm: Runnable) -> dict:
    resp: AIMessage = await llm.ainvoke({"messages": state["messages"]})
    return {"messages": [resp]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END

async def create_openai_agent(server_name: str = "mouse") -> Runnable:
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
            "mouse": {
                "transport": "streamable_http",
                "url": "http://localhost:8001/mouse/mcp"
            },
            "gamepad": {
                "transport": "streamable_http",
                "url": "http://localhost:8001/gamepad/mcp"
            }
        }
    )

    tools = await client.get_tools(server_name=server_name)

    llm = AzureChatOpenAI(
        azure_deployment=openai_model,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-05-01-preview"
        ),
        temperature=0,
    ).bind_tools(tools)

    llm: Runnable = prompt | llm

    async def agent_wrapper(state: AgentState) -> dict:
        return await agent_node(state, llm)
    
    agent_node_lambda = RunnableLambda(agent_wrapper).with_config({"run_name": "agent_node"})
    tools_node = ToolNode(tools=tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node_lambda)
    graph.add_node("tools", tools_node)
    graph.add_node("promote_images", promote_images_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "promote_images")
    graph.add_edge("promote_images", "agent")

    compiled_graph = graph.compile()
    return compiled_graph

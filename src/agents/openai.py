from typing import Dict, List, Optional
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os
from .utils import load_agent_prompt


async def create_openai_agent(
    model: str = "gpt-4o-mini",
    server_name: str = "mouse",
):
    """Create and fully initialize an OpenAI BalatroAgent instance."""
    load_dotenv()
            
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    assert (
        azure_endpoint and openai_api_key and openai_api_version
    ), "Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_API_VERSION in your environment variables."

    llm = AzureChatOpenAI(
        azure_deployment=model,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-05-01-preview"
        ),
        temperature=0,
    )

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

    system_prompt = load_agent_prompt(control_type=server_name)

    agent = create_react_agent(
        model=llm,
        tools=tools,
        debug=False,
        prompt=system_prompt,
    )

    return agent, tools
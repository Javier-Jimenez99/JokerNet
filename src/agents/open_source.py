from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from .utils import load_agent_prompt, create_hermes_system_message
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from typing import Dict, List, Optional
import os


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

        system_contents = create_hermes_system_message(tools)
        system_contents.append({"type": "text", "text": load_agent_prompt()})

        self.agent = create_react_agent(
            model=llm,
            tools=tools,
            debug=False,
            prompt=SystemMessage(content=system_contents),
        )

    async def ainvoke(self, messages) -> Dict:
        """Invoke the agent with a message and return the response."""
        if self.agent is None:
            raise RuntimeError(
                "Agent not initialized. Use BalatroAgent.create() instead of BalatroAgent()"
            )

        # ✅ CONFIGURAR: Límite de recursión/iteraciones
        return await self.agent.ainvoke(
            messages,
            config={
                "recursion_limit": self.max_iterations,  # Máximo de iteraciones
                "configurable": {"max_iterations": self.max_iterations},
            },
        )

from typing import Dict
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os


def load_agent_prompt() -> str:
    """Load the agent prompt from a file."""
    with open("prompts/general_prompt.txt", "r") as file:
        return file.read()

class OpenAIBalatroAgent:
    def __init__(self):
        """Initialize the agent synchronously. Use create() for full setup."""
        self.agent = None
        self.max_iterations = 20  
    
    @classmethod
    async def create(cls, model: str = "gpt-4o-mini", mcp_url: str = "http://localhost:8001/mcp", max_iterations: int = 10):
        """Create and fully initialize a BalatroAgent instance."""
        instance = cls()
        instance.max_iterations = max_iterations  # ✅ Permitir configuración personalizada
        await instance._initialize(model, mcp_url)
        return instance
    
    async def _initialize(self, model: str, mcp_url: str):
        """Internal async initialization method."""
        load_dotenv()
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        assert azure_endpoint and openai_api_key and openai_api_version, "Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_API_VERSION in your environment variables."

        llm = AzureChatOpenAI(
            azure_deployment=model,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
            temperature=0,
        )

        client = MultiServerMCPClient(
            {
                "balatro": {
                    "transport": "streamable_http",
                    "url": mcp_url,
                },
            }
        )

        self.agent = create_react_agent(
            model=llm,
            tools=await client.get_tools(),
            debug=False,
            prompt=load_agent_prompt(),
        )
    
    async def ainvoke(self, messages) -> Dict:
        """Invoke the agent with a message and return the response."""
        if self.agent is None:
            raise RuntimeError("Agent not initialized. Use BalatroAgent.create() instead of BalatroAgent()")
        
        # ✅ CONFIGURAR: Límite de recursión/iteraciones
        return await self.agent.ainvoke(
            messages,
            config={
                "recursion_limit": self.max_iterations,  # Máximo de iteraciones
                "configurable": {
                    "max_iterations": self.max_iterations
                }
            }
        )
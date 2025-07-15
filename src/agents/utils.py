from langchain.agents import tool
from langchain_core.messages import SystemMessage
from qwen_agent.llm.fncall_prompts.nous_fncall_prompt import (
    NousFnCallPrompt,
    Message,
    ContentItem,
)


def langchain_tools_to_qwen_functions(langchain_tools):
    """Convierte herramientas de LangChain al formato de funciones de QWen Agent"""
    functions = []

    for tool in langchain_tools:
        # Obtener el esquema de argumentos de la herramienta
        args_schema = tool.args_schema.schema() if hasattr(tool, "args_schema") else {}

        # Crear la definición de función en el formato esperado por QWen
        function_def = {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": args_schema.get("properties", {}),
                "required": args_schema.get("required", []),
            },
        }

        functions.append(function_def)

    return functions


def create_hermes_system_message(tools) -> list:
    """
    Create a system message with Hermes format using the provided langchain tools.

    Parameters
    ----------
    tools : list
        List of LangChain tools to include in the system message.

    Returns
    -------
    list
        A list containing the system message in Hermes format.
    """

    qwen_functions = langchain_tools_to_qwen_functions(tools)

    system_message = NousFnCallPrompt().preprocess_fncall_messages(
        messages=[
            Message(
                role="system",
                content=[ContentItem(text="You are a helpful assistant.")],
            ),
        ],
        functions=qwen_functions,
        lang=None,
    )

    system_message = system_message[0].model_dump()
    contents = [
        {"type": "text", "text": msg["text"]} for msg in system_message["content"]
    ]

    return contents


def load_agent_prompt() -> str:
    """Load the agent prompt from a file."""
    with open("prompts/general_prompt.txt", "r") as file:
        return file.read()

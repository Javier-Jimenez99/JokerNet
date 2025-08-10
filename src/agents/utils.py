from qwen_agent.llm.fncall_prompts.nous_fncall_prompt import (
    NousFnCallPrompt,
    Message,
    ContentItem,
)
from jinja2 import Environment, FileSystemLoader


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


def load_agent_prompt(control_type: str = "mouse") -> str:
    """Load and render the agent prompt from Jinja templates."""
    prompts_dir = "./prompts"
    
    # Configurar el entorno de Jinja2
    env = Environment(loader=FileSystemLoader(prompts_dir))
    
    # Cargar el template principal
    general_template = env.get_template("general.jinja")
    
    # Cargar el template de controles específico
    if control_type == "mouse":
        controls_template = env.get_template("controls/mouse.jinja")
    elif control_type == "gamepad":
        controls_template = env.get_template("controls/gamepad.jinja")
    else:
        raise ValueError(f"Unsupported control type: {control_type}")
    
    # Renderizar el template de controles
    controls_content = controls_template.render()
    
    # Renderizar el template principal con los controles
    full_prompt = general_template.render(controls=controls_content)
    
    return full_prompt

def load_summary_prompt() -> str:
    """Load and render the summary prompt from Jinja templates."""
    prompts_dir = "./prompts"
    
    # Configurar el entorno de Jinja2
    env = Environment(loader=FileSystemLoader(prompts_dir))
    
    # Cargar el template de resumen
    summary_template = env.get_template("summary.jinja")    

    # Renderizar el template de resumen
    summary_content = summary_template.render()

    return summary_content
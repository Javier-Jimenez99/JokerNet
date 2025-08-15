from __future__ import annotations
from typing import TypedDict, Optional, List, Dict, Any, Literal
from functools import partial
import os, json, time

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AnyMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    task: str
    last_screenshot: Optional[HumanMessage]
    screen_descriptions: List[str]
    consecutive_duplicates: int
    history_messages: List[AnyMessage]
    history_limit: int
    ai_message: Optional[AIMessage]
    done: bool
    result: Optional[Dict[str, Any]]
    recursion_count: int
    max_recursions: int

def clamp_history(msgs: List[AnyMessage], limit: int) -> List[AnyMessage]:
    """Mantiene historial completo pero filtra imágenes antiguas (excepto la última)"""
    if len(msgs) <= limit:
        return msgs
    
    # Separa mensajes con y sin imágenes
    filtered_msgs = []
    last_image_msg = None
    
    for msg in msgs:
        has_image = False
        if hasattr(msg, 'content') and isinstance(msg.content, list):
            has_image = any(item.get('type') == 'image_url' for item in msg.content)
        
        if has_image:
            last_image_msg = msg  # Mantén solo la última imagen
        else:
            filtered_msgs.append(msg)  # Mantén todos los mensajes sin imagen
    
    # Añade la última imagen al final si existe
    if last_image_msg:
        filtered_msgs.append(last_image_msg)
    
    # Si aún excede el límite, mantén los más recientes
    return filtered_msgs[-limit:] if len(filtered_msgs) > limit else filtered_msgs

def descriptions_are_similar(desc1: str, desc2: str) -> bool:
    """Simple similarity check based on description content"""
    if not desc1 or not desc2:
        return False
    
    clean1 = desc1.lower().strip()
    clean2 = desc2.lower().strip()
    
    words1 = set(clean1.split())
    words2 = set(clean2.split())
    
    if not words1 or not words2:
        return False
        
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    similarity = intersection / union if union > 0 else 0
    
    return similarity > 0.8

def ANALYZER_PROMPT() -> str:
    return """You are a Screen Analyzer. Provide a concise description of the current game state.

Focus on:
- Main UI elements visible
- Current game context (menu, gameplay, dialog)
- Key actionable elements
- Cards in hand that can be clickable

Respond with a simple description (1-2 sentences max). Be consistent in terminology."""

def WORKER_PROMPT() -> str:
    return """You are a Balatro Game Controller.

You receive:
- Screenshot of current game state
- Task to accomplish
- History of all screen descriptions
- Count of consecutive duplicate screens

REASONING PROCESS (Chain of Thought):
First, analyze the situation step by step:
1. CURRENT STATE: What do I see in the screenshot?
2. TASK PROGRESS: How does this relate to my assigned task?
3. SCREEN HISTORY: Have I seen similar screens recently? Are we making progress?
4. NEXT ACTION: What should I do next?

Then decide:

TERMINATION RULES:
- If consecutive_duplicates >= 3: Reply TASK_DONE {"success": false, "reason": "stuck"}
- If task completed: Reply TASK_DONE {"success": true, "reason": "completed"}
- If task impossible: Reply TASK_DONE {"success": false, "reason": "impossible"}

FORMAT:
Think step by step, then either:
1. Call exactly ONE control tool, OR  
2. Reply TASK_DONE with reasoning

Example reasoning:
"CURRENT STATE: I see the main menu with a 'Start' button.
TASK PROGRESS: My task is to start the game, and the Start button is visible.
SCREEN HISTORY: This is the first screen I've seen.
NEXT ACTION: I should click the Start button to complete the task."

Then take action or terminate."""

async def capture_node(state: AgentState, screenshot_tool) -> dict:
    current_count = state.get("recursion_count", 0) + 1
    max_rec = state.get("max_recursions", 120)
    
    if current_count > max_rec:
        return {"done": True, "result": {"success": False, "reason": "max_iterations"}, "recursion_count": current_count}
    
    try:
        res = await screenshot_tool.ainvoke({})
        data = json.loads(res) if isinstance(res, str) else res
        img = data.get("screenshot", "")
        mouse_info = data.get("mouse_info", "")
        
        screenshot = HumanMessage(content=[
            {"type": "text", "text": f"{mouse_info} Current game state:"},
            {"type": "image_url", "image_url": {"url": img}}
        ])
        return {"last_screenshot": screenshot, "recursion_count": current_count}
    except Exception as e:
        return {"last_screenshot": None, "recursion_count": current_count}

async def analyze_node(state: AgentState, llm_analyzer) -> dict:
    iteration = state.get("recursion_count", 0)
    screenshot = state.get("last_screenshot")
    
    if not screenshot:
        return {}
    
    try:
        msgs = [SystemMessage(content=ANALYZER_PROMPT()), screenshot]
        resp = await llm_analyzer.ainvoke(
            msgs, 
            config={
                "metadata": {
                    "node": "analyze", 
                    "iteration": iteration,
                    "task": state.get("task", "")[:50]
                }
            }
        )
        current_description = resp.content.strip()
    except Exception as e:
        current_description = "Analysis failed"
    
    descriptions = state.get("screen_descriptions", [])
    last_description = descriptions[-1] if descriptions else ""
    
    is_duplicate = descriptions_are_similar(current_description, last_description)
    consecutive_duplicates = state.get("consecutive_duplicates", 0)
    consecutive_duplicates = consecutive_duplicates + 1 if is_duplicate else 0
    
    descriptions.append(current_description)
    if len(descriptions) > 10:
        descriptions = descriptions[-10:]
    
    return {
        "screen_descriptions": descriptions,
        "consecutive_duplicates": consecutive_duplicates
    }

async def worker_node(state: AgentState, llm_worker) -> dict:
    iteration = state.get("recursion_count", 0)

    msgs = [SystemMessage(content=WORKER_PROMPT())]
    msgs.append(HumanMessage(
        content=f"This is your task: \n{state.get('task', '')}"
    ))
    
    # Format screen descriptions safely
    screen_descriptions = state.get('screen_descriptions', [])
    descriptions_text = '\n'.join(screen_descriptions)
    msgs.append(HumanMessage(
        content=f"These are the previous screens states: \n{descriptions_text}"
    ))

    # Incluir todo el historial de herramientas y resultados
    history = state.get("history_messages", [])
    msgs.extend(history)
    
    # Añadir la screenshot actual
    if state.get("last_screenshot"):
        msgs.append(state["last_screenshot"])
    
    resp = await llm_worker.ainvoke(
        msgs,
        config={
            "metadata": {
                "node": "worker",
                "iteration": iteration,
                "task": state.get("task", "")[:50],
                "consecutive_duplicates": state.get("consecutive_duplicates", 0),
                "history_count": len(history)
            }
        }
    )
    
    return {"ai_message": resp}

def route_after_capture(state: AgentState) -> Literal["analyze", "end"]:
    return "end" if state.get("done", False) else "analyze"

def route_after_analyze(state: AgentState) -> Literal["worker"]:
    return "worker"

def route_after_worker(state: AgentState) -> Literal["tool", "finalize"]:
    ai = state.get("ai_message")
    return "tool" if (ai and ai.tool_calls) else "finalize"

async def tool_node(state: AgentState, toolnode: ToolNode) -> dict:
    ai = state.get("ai_message")
    if not ai or not ai.tool_calls:
        return {}
    
    try:
        tool_msgs = await toolnode.ainvoke([ai])
        if not isinstance(tool_msgs, list):
            tool_msgs = [tool_msgs]
        
        history = state.get("history_messages", [])
        history.extend([ai] + tool_msgs)
        history = clamp_history(history, state.get("history_limit", 20))
        
        # Limpiar el ai_message para que no interfiera con el próximo routing
        return {"history_messages": history, "ai_message": None}
        
    except Exception as e:
        return {}

def finalize_node(state: AgentState) -> dict:
    ai = state.get("ai_message")
    txt = (ai.content or "").strip() if ai else ""
    iteration = state.get("recursion_count", 0)
    screen_descriptions = state.get("screen_descriptions", [])
    task = state.get("task", "")
    
    final_description = screen_descriptions[-1] if screen_descriptions else "No screen analyzed"
    
    # Extract reasoning from worker response
    reasoning = ""
    if txt and not txt.startswith("TASK_DONE"):
        reasoning = txt[:200] + "..." if len(txt) > 200 else txt
    
    if txt.startswith("TASK_DONE"):
        try:
            json_part = txt.split("TASK_DONE", 1)[1].strip()
            result = json.loads(json_part)
            result["iterations"] = iteration
            result["description"] = f"Task '{task}': {result.get('reason')} after {iteration} iterations. Final: {final_description}"
            if reasoning:
                result["worker_reasoning"] = reasoning
        except:
            result = {
                "success": True, 
                "reason": "completed", 
                "iterations": iteration,
                "description": f"Task '{task}': completed after {iteration} iterations. Final: {final_description}"
            }
    else:
        result = {
            "success": False, 
            "reason": "no_action", 
            "iterations": iteration,
            "description": f"Task '{task}': no action after {iteration} iterations. Final: {final_description}",
            "worker_reasoning": reasoning if reasoning else "No reasoning provided"
        }
    
    return {"done": True, "result": result}

async def create_worker(server_name: str = "mouse"):
    llm_worker = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        temperature=0,
    )
    
    llm_analyzer = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        temperature=0,
    )

    client = MultiServerMCPClient({
        "mouse": {"transport":"streamable_http", "url":"http://localhost:8001/mouse/mcp"},
        "gamepad": {"transport":"streamable_http", "url":"http://localhost:8001/gamepad/mcp"}
    })
    tools = await client.get_tools(server_name=server_name)

    screenshot_tool, control_tools = None, []
    for t in tools:
        tool_name = getattr(t, "name", "")
        if tool_name == "get_screen":
            screenshot_tool = t
        else:
            control_tools.append(t)
    
    llm_worker = llm_worker.bind_tools(control_tools)
    toolnode = ToolNode(tools=control_tools)

    graph = StateGraph(AgentState)
    graph.add_node("capture", partial(capture_node, screenshot_tool=screenshot_tool))
    graph.add_node("analyze", partial(analyze_node, llm_analyzer=llm_analyzer))
    graph.add_node("worker", partial(worker_node, llm_worker=llm_worker))
    graph.add_node("tool", partial(tool_node, toolnode=toolnode))
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "capture")
    graph.add_conditional_edges("capture", route_after_capture, {"analyze": "analyze", "end": END})
    graph.add_conditional_edges("analyze", route_after_analyze, {"worker": "worker"})
    graph.add_conditional_edges("worker", route_after_worker, {"tool": "tool", "finalize": "finalize"})
    graph.add_edge("tool", "capture")
    graph.add_edge("finalize", END)

    return graph.compile()

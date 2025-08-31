from langgraph.graph import StateGraph, START, END
from langchain_mcp_adapters.client import MultiServerMCPClient
from functools import partial
from langgraph.prebuilt import ToolNode
from langchain_openai import AzureChatOpenAI
import os
import json
import time
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .models import PlannerResponse, GameState, AgentState
from .prompts import visualizer_system_prompt, worker_system_prompt, planner_system_prompt
from typing import Literal

load_dotenv()

async def get_tools(server_name: str="gamepad"):
    client = MultiServerMCPClient({
        "mouse": {"transport":"streamable_http", "url":"http://localhost:8001/mouse/mcp"},
        "gamepad": {"transport":"streamable_http", "url":"http://localhost:8001/gamepad/mcp"}
    })
    
    # Get tools for the specified server
    tools = await client.get_tools(server_name=server_name)

    screenshot_tool, control_tools = None, []
    for t in tools:
        tool_name = getattr(t, "name", "")
        if tool_name == "get_screen" or tool_name == "get_screen_with_cursor":
            screenshot_tool = t
        else:
            control_tools.append(t)

    return screenshot_tool, control_tools


async def create_llm(structured_output_class=None, model:str="gpt-4.1", reasoning_effort: str = "minimal", tools = None):
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=model,
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        reasoning_effort=reasoning_effort
    )
    
    if structured_output_class is not None:
        llm = llm.with_structured_output(structured_output_class)

    if tools is not None:
        llm = llm.bind_tools(tools)

    return llm

async def visualizer_node(state: AgentState, screenshot_tool, llm):
    game_states = state.get("game_states", [])
    res = await screenshot_tool.ainvoke({})
    data = json.loads(res) if isinstance(res, str) else res
    img = data.get("screenshot", "")

    messages = [SystemMessage(content=visualizer_system_prompt)]

    if len(game_states) > 0:
        last_game_state = game_states[-1]
        messages.append(HumanMessage(content=[
            {"type": "text", "text": f"This is the previous game state: \n{last_game_state}"}
        ]))
    
    messages.append(HumanMessage(content=[
        {"type": "text", "text": "Extract all the relevant information of this game screenshot."},
        {"type": "image_url", "image_url": {"url": img}}
    ]))

    response = await llm.ainvoke(messages)
    json_state = response.model_dump_json(indent=2)
    game_states.append(json_state)

    return {
        "game_states": game_states,
        "last_screenshot": img
    }

async def worker_node(state: AgentState, llm):
    worker_responses = state["worker_responses"]
    messages = [
        SystemMessage(content=worker_system_prompt)
    ]

    last_subtask = state.get("subtasks", [])[-1].subtask

    messages.append(HumanMessage(content=[
        {"type": "text", "text": f"This is the current game state: \n{state.get("game_states", [])[-1]}"},
        {"type": "image_url", "image_url": {"url": state.get("last_screenshot", "")}},
        {"type": "text", "text": f"Your task is: {last_subtask}"}
    ]))

    response = await llm.ainvoke(messages)
    worker_responses.append(response)

    return {
        "worker_responses": worker_responses,
        "worker_step": state["worker_step"] + 1
    }

def parse_worker_responses(responses):
    last_response = responses[-1]
    if last_response.tool_calls:
        return "The worker did not solve the task, try to simplify it."
    else:
        return last_response.content

async def planner_node(state: AgentState, llm) -> dict:
    game_states = state.get("game_states", [])
    subtasks = state.get("subtasks", [])
    messages = [
        SystemMessage(content=planner_system_prompt)
    ]

    messages.extend(state.get("input", []))

    messages.append(HumanMessage(content=[
        {"type": "text", "text": f"This is the current game state: \n{game_states[-1]}"},
        {"type": "image_url", "image_url": {"url": state["last_screenshot"]}}
    ]))

    if len(subtasks) > 0:
        last_subtask = subtasks[-1]
        worker_result = parse_worker_responses(state["worker_responses"])
        messages.append(HumanMessage(content=[
            {"type": "text", "text": f"This is the last subtask you assigned to the worker: \n{last_subtask.subtask}"},
            {"type": "text", "text": f"This is the result of the last subtask executed by the worker: \n{worker_result}"},
            {"type": "text", "text": "Keep working on the main task if it is not finished yet."}
        ]))

    response = await llm.ainvoke(messages)

    subtasks.append(response)

    return {
        "subtasks": subtasks,
        "worker_step": 0,
        "worker_responses": [],
        "planner_step": state.get("planner_step", 0) + 1
    }

async def tool_node(state:AgentState, toolnode:ToolNode) -> dict:
    messages = state.get("worker_responses", [])  # Lista completa
    
    # El ToolNode busca automáticamente el último AIMessage con tool_calls
    tool_msgs = await toolnode.ainvoke(messages)

    time.sleep(2)
    
    return {"messages": messages + tool_msgs}

async def output_node(state:AgentState) -> dict:
    subtasks = state.get("subtasks", [])
    if len(subtasks) == 0:
        return {"output": AIMessage("There was an error and no subtasks were executed.")}

    last_subtask = subtasks[-1]
    if last_subtask.action == "finish" and last_subtask.summary:
        return {"output": AIMessage(last_subtask.summary)}

    error_msg = "The task could not be finished yet. But these were the subtasks tried:"
    for subtask in subtasks:
        error_msg += f"- {subtask.subtask}\n"

    return {"output": AIMessage(error_msg)}


def route_after_planner(state: AgentState, max_planner_steps:int) -> Literal["worker_visualizer", "end"]:
    if state["planner_step"] >= max_planner_steps:
        return "end"

    return "worker_visualizer" if state["subtasks"][-1].action == "delegate" else "end"

def route_after_worker(state: AgentState, max_worker_steps:int) -> Literal["tool", "planner"]:
    if state["worker_step"] >= max_worker_steps:
        return "planner"

    return "tool" if state["worker_responses"][-1].tool_calls else "planner"

async def create_agent(max_worker_steps:int = 3, max_planner_steps:int = 5, server_name:str="gamepad"):
    screenshot_tool, control_tools = await get_tools(server_name=server_name)
    llm_visualizer = await create_llm(
        structured_output_class=GameState,
        model="gpt-5-mini",
        reasoning_effort="minimal"
    )

    llm_worker = await create_llm(
        model="gpt-5-mini",
        reasoning_effort="low",
        tools=control_tools
    )

    llm_planner = await create_llm(
        model="gpt-5-mini",
        reasoning_effort="medium",
        structured_output_class=PlannerResponse
    )

    toolnode = ToolNode(tools=control_tools)

    graph = StateGraph(AgentState)

    # === PLANNER NODES ===
    graph.add_node("planner_visualizer", partial(visualizer_node, screenshot_tool=screenshot_tool, llm=llm_visualizer))
    graph.add_node("planner", partial(planner_node, llm=llm_planner))

    # === WORKER NODES ===
    graph.add_node("worker_visualizer", partial(visualizer_node, screenshot_tool=screenshot_tool, llm=llm_visualizer))
    graph.add_node("worker", partial(worker_node, llm=llm_worker))
    graph.add_node("tool", partial(tool_node, toolnode=toolnode))

    graph.add_node("output", output_node)

    # === EDGES ===
    graph.add_edge(START, "planner_visualizer")
    graph.add_edge("planner_visualizer", "planner")
    graph.add_edge("worker_visualizer", "worker")
    graph.add_edge("tool", "worker_visualizer")
    graph.add_edge("output", END)

    graph.add_conditional_edges(
        "planner", 
        partial(route_after_planner, max_planner_steps=max_planner_steps), 
        {"worker_visualizer": "worker_visualizer", "end": "output"}
    )
    graph.add_conditional_edges(
        "worker", 
        partial(route_after_worker, max_worker_steps=max_worker_steps), 
        {"tool": "tool", "planner": "planner"}
    )

    return graph.compile()
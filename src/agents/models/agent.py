from typing_extensions import TypedDict
from langchain_core.messages import AIMessage, BaseMessage
from .planner import PlannerResponse


class AgentState(TypedDict):
    input: list[BaseMessage]
    game_states: list[str]
    worker_responses: list[str]
    last_screenshot: str
    worker_step: int
    planner_step: int
    subtasks: list[PlannerResponse]
    output: AIMessage
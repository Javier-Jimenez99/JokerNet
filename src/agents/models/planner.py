from pydantic import BaseModel, Field
from typing import Literal, Optional

class PlannerResponse(BaseModel):
    """Response from the planner that can either delegate to worker or finish conversation."""
    action: Literal["delegate", "finish"] = Field(..., description="The action to take: 'delegate' to assign a task to the worker, or 'finish' to end the conversation.")
    reasoning: str = Field(..., description="The reasoning behind the chosen action.")
    subtask: Optional[str] = Field(None, description="The simple, actionable instruction for the worker (required when action='delegate').")
    summary: Optional[str] = Field(None, description="A comprehensive summary of how the task was completed (required when action='finish').")

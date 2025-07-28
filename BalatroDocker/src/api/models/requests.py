"""
Pydantic models for API request and response validation.
"""
from typing import Optional, List
from pydantic import BaseModel


class GamepadButtonsRequest(BaseModel):
    """Request model for gamepad button presses."""
    buttons: str = "A"
    step_id: Optional[str] = None
    duration: Optional[float] = 0.1
    
    class Config:
        json_schema_extra = {
            "example": {
                "buttons": "A B",
                "step_id": "step_1",
                "duration": 0.1
            }
        }


class MouseClickRequest(BaseModel):
    """Request model for mouse clicks."""
    x: float  # Relative coordinate (0-1)
    y: float  # Relative coordinate (0-1)
    button: str = "left"
    clicks: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "x": 0.5,
                "y": 0.5,
                "button": "left",
                "clicks": 1
            }
        }


class MouseMoveRequest(BaseModel):
    """Request model for mouse movement."""
    x: float  # Relative coordinate (0-1)
    y: float  # Relative coordinate (0-1)
    duration: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "x": 0.5,
                "y": 0.5,
                "duration": 0.5
            }
        }


class MouseDragRequest(BaseModel):
    """Request model for mouse dragging."""
    start_x: float  # Relative coordinate (0-1)
    start_y: float  # Relative coordinate (0-1)
    end_x: float    # Relative coordinate (0-1)
    end_y: float    # Relative coordinate (0-1)
    duration: float = 0.5
    button: str = "left"
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_x": 0.3,
                "start_y": 0.3,
                "end_x": 0.7,
                "end_y": 0.7,
                "duration": 0.5,
                "button": "left"
            }
        }


class AutoStartRequest(BaseModel):
    """Request model for auto-starting the game."""
    deck: Optional[str] = "b_red"
    stake: Optional[int] = 1
    seed: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "deck": "b_red",
                "stake": 1,
                "seed": "12345"
            }
        }

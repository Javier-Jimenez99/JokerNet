"""
Mouse input controller for handling mouse actions and positioning.
"""
import pyautogui
from typing import Dict, Any
from fastapi import HTTPException

from api.models.requests import MouseClickRequest, MouseMoveRequest, MouseDragRequest
from api.utils.system import relative_to_absolute


async def mouse_click(request: MouseClickRequest) -> Dict[str, Any]:
    """Click at specific coordinates using relative positioning (0-1)."""
    try:
        # Get screen dimensions and convert coordinates
        screen_width, screen_height = pyautogui.size()
        abs_x, abs_y = relative_to_absolute(request.x, request.y, screen_width, screen_height)
        
        pyautogui.click(abs_x, abs_y, clicks=request.clicks, button=request.button)
        return {
            "status": "success",
            "message": f"Clicked at relative ({request.x:.3f}, {request.y:.3f}) -> absolute ({abs_x}, {abs_y}) with {request.button} button {request.clicks} time(s)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to click: {str(e)}")


async def mouse_move(request: MouseMoveRequest) -> Dict[str, Any]:
    """Move mouse cursor to specific coordinates using relative positioning (0-1)."""
    try:
        # Get screen dimensions and convert coordinates
        screen_width, screen_height = pyautogui.size()
        abs_x, abs_y = relative_to_absolute(request.x, request.y, screen_width, screen_height)
        
        pyautogui.moveTo(abs_x, abs_y, duration=request.duration)
        return {
            "status": "success",
            "message": f"Moved mouse to relative ({request.x:.3f}, {request.y:.3f}) -> absolute ({abs_x}, {abs_y})"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move mouse: {str(e)}")


async def mouse_drag(request: MouseDragRequest) -> Dict[str, Any]:
    """Drag from start coordinates to end coordinates using relative positioning (0-1)."""
    try:
        # Get screen dimensions and convert coordinates
        screen_width, screen_height = pyautogui.size()
        abs_start_x, abs_start_y = relative_to_absolute(request.start_x, request.start_y, screen_width, screen_height)
        abs_end_x, abs_end_y = relative_to_absolute(request.end_x, request.end_y, screen_width, screen_height)
        
        pyautogui.drag(
            abs_end_x - abs_start_x,
            abs_end_y - abs_start_y,
            duration=request.duration,
            button=request.button,
            start=(abs_start_x, abs_start_y)
        )
        return {
            "status": "success",
            "message": f"Dragged from relative ({request.start_x:.3f}, {request.start_y:.3f}) -> absolute ({abs_start_x}, {abs_start_y}) to relative ({request.end_x:.3f}, {request.end_y:.3f}) -> absolute ({abs_end_x}, {abs_end_y}) with {request.button} button"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to drag: {str(e)}")


async def get_mouse_position() -> Dict[str, Any]:
    """Get current mouse position in both absolute and relative coordinates."""
    try:
        # Get absolute position
        abs_x, abs_y = pyautogui.position()
        
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        # Calculate relative position
        rel_x = abs_x / screen_width if screen_width > 0 else 0
        rel_y = abs_y / screen_height if screen_height > 0 else 0
        
        return {
            "absolute": {"x": abs_x, "y": abs_y},
            "relative": {"x": round(rel_x, 6), "y": round(rel_y, 6)},
            "screen_size": {"width": screen_width, "height": screen_height},
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mouse position: {str(e)}")

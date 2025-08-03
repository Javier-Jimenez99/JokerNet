"""
Mouse input controller for handling mouse actions and positioning.
"""
import pyautogui
from typing import Dict, Any
from fastapi import HTTPException

from api.models.requests import MouseClickRequest, MouseMoveRequest, MouseDragRequest
from api.utils.system import relative_to_absolute


async def mouse_click(request: MouseClickRequest) -> Dict[str, Any]:
    """Click at specific coordinates using pixel positioning."""
    try:
        # Get screen dimensions for validation and info
        screen_width, screen_height = pyautogui.size()
        
        # Use coordinates directly as pixels
        pixel_x, pixel_y = int(request.x), int(request.y)
        
        pyautogui.click(pixel_x, pixel_y, clicks=request.clicks, button=request.button)
        return {
            "status": "success",
            "message": f"Clicked at pixel coordinates ({pixel_x}, {pixel_y}) with {request.button} button {request.clicks} time(s)",
            "screen_size": {"width": screen_width, "height": screen_height},
            "coordinate_info": f"Screen resolution: {screen_width}x{screen_height} pixels. Use pixel coordinates for all mouse actions."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to click: {str(e)}")


async def mouse_move(request: MouseMoveRequest) -> Dict[str, Any]:
    """Move mouse cursor to specific coordinates using pixel positioning."""
    try:
        # Get screen dimensions for validation and info
        screen_width, screen_height = pyautogui.size()
        
        # Use coordinates directly as pixels
        pixel_x, pixel_y = int(request.x), int(request.y)
        
        pyautogui.moveTo(pixel_x, pixel_y, duration=request.duration)
        return {
            "status": "success",
            "message": f"Moved mouse to pixel coordinates ({pixel_x}, {pixel_y})",
            "screen_size": {"width": screen_width, "height": screen_height},
            "coordinate_info": f"Screen resolution: {screen_width}x{screen_height} pixels. Use pixel coordinates for all mouse actions."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move mouse: {str(e)}")


async def mouse_drag(request: MouseDragRequest) -> Dict[str, Any]:
    """Drag from start coordinates to end coordinates using pixel positioning."""
    try:
        # Get screen dimensions for validation and info
        screen_width, screen_height = pyautogui.size()
        
        # Use coordinates directly as pixels
        start_x, start_y = int(request.start_x), int(request.start_y)
        end_x, end_y = int(request.end_x), int(request.end_y)
        
        pyautogui.drag(
            end_x - start_x,
            end_y - start_y,
            duration=request.duration,
            button=request.button,
            start=(start_x, start_y)
        )
        return {
            "status": "success",
            "message": f"Dragged from pixel coordinates ({start_x}, {start_y}) to ({end_x}, {end_y}) with {request.button} button",
            "screen_size": {"width": screen_width, "height": screen_height},
            "coordinate_info": f"Screen resolution: {screen_width}x{screen_height} pixels. Use pixel coordinates for all mouse actions."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to drag: {str(e)}")


async def get_mouse_position() -> Dict[str, Any]:
    """Get current mouse position in pixel coordinates."""
    try:
        # Get absolute position in pixels
        pixel_x, pixel_y = pyautogui.position()
        
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        return {
            "position": {"x": pixel_x, "y": pixel_y},
            "screen_size": {"width": screen_width, "height": screen_height},
            "coordinate_info": f"Mouse at pixel coordinates ({pixel_x}, {pixel_y}). Screen resolution: {screen_width}x{screen_height} pixels.",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mouse position: {str(e)}")

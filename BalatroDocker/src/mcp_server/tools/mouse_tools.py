"""
Mouse tools for MCP server integration.
"""
import requests
from fastmcp.utilities.types import Image

FASTAPI_URL = "http://localhost:8000"


def get_mouse_position() -> dict:
    """
    Get the current mouse position in both absolute and relative coordinates.
    
    Returns:
        dict: Dictionary containing absolute coordinates, relative coordinates (0-1), and screen size
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/mouse/position", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def mouse_click(x: float, y: float, button: str = "left", clicks: int = 1) -> dict:
    """
    Click at a specific coordinate on the screen using relative coordinates.
    
    Args:
        x (float): Relative X coordinate (0.0 = left edge, 1.0 = right edge)
        y (float): Relative Y coordinate (0.0 = top edge, 1.0 = bottom edge)
        button (str): Mouse button to click ('left', 'right', 'middle')
        clicks (int): Number of clicks (default: 1)
    
    Returns:
        dict: Status of the click operation
    """
    try:
        payload = {
            "x": x,
            "y": y,
            "button": button,
            "clicks": clicks
        }
        
        response = requests.post(f"{FASTAPI_URL}/mouse/click", json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def mouse_move(x: float, y: float, duration: float = 0.0) -> dict:
    """
    Move the mouse cursor to a specific coordinate using relative coordinates.
    
    Args:
        x (float): Relative X coordinate (0.0 = left edge, 1.0 = right edge)
        y (float): Relative Y coordinate (0.0 = top edge, 1.0 = bottom edge)
        duration (float): Duration of the movement in seconds (default: 0.0 for instant)
    
    Returns:
        dict: Status of the move operation
    """
    try:
        payload = {
            "x": x,
            "y": y,
            "duration": duration
        }
        
        response = requests.post(f"{FASTAPI_URL}/mouse/move", json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def mouse_drag(start_x: float, start_y: float, end_x: float, end_y: float, duration: float = 0.5, button: str = "left") -> dict:
    """
    Drag the mouse from start coordinates to end coordinates using relative coordinates.
    
    Args:
        start_x (float): Starting relative X coordinate (0.0 = left edge, 1.0 = right edge)
        start_y (float): Starting relative Y coordinate (0.0 = top edge, 1.0 = bottom edge)
        end_x (float): Ending relative X coordinate (0.0 = left edge, 1.0 = right edge)
        end_y (float): Ending relative Y coordinate (0.0 = top edge, 1.0 = bottom edge)
        duration (float): Duration of the drag in seconds (default: 0.5)
        button (str): Mouse button to use for dragging ('left', 'right', 'middle')
    
    Returns:
        dict: Status of the drag operation
    """
    try:
        payload = {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "duration": duration,
            "button": button
        }
        
        response = requests.post(f"{FASTAPI_URL}/mouse/drag", json=payload, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def get_screen_with_cursor() -> Image:
    """
    Get a screenshot with the current mouse cursor position highlighted.
    
    Returns:
        ImageContent: Screenshot with cursor crosshair visible
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/screenshot_with_cursor", timeout=10)

        if response.status_code != 200:
            raise RuntimeError(f"Screenshot backend error: HTTP {response.status_code} - {response.text}")

        return Image(data=response.content, format="png")
        
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to get screenshot with cursor: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")

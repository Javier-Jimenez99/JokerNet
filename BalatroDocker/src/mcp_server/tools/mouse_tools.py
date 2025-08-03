"""
Mouse tools for MCP server integration.
"""
import requests
from fastmcp.utilities.types import Image

FASTAPI_URL = "http://localhost:8000"


def get_screen_dimensions() -> dict:
    """
    Get current screen dimensions.
    
    Returns:
        dict: Dictionary containing screen width and height
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/mouse/position", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("screen_size", {"width": 1920, "height": 1080})
        else:
            # Fallback dimensions if request fails
            return {"width": 1920, "height": 1080}
    except Exception:
        # Fallback dimensions if request fails
        return {"width": 1920, "height": 1080}


def get_mouse_position() -> dict:
    """
    Get the current mouse position in pixel coordinates.
    
    Returns:
        dict: Dictionary containing pixel coordinates and screen size
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


def mouse_click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
    """
    Click at a specific coordinate on the screen using pixel coordinates.
    
    Args:
        x (int): X coordinate in pixels
        y (int): Y coordinate in pixels
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


def mouse_move(x: int, y: int, duration: float = 0.0) -> dict:
    """
    Move the mouse cursor to a specific coordinate using pixel coordinates.
    
    Args:
        x (int): X coordinate in pixels
        y (int): Y coordinate in pixels
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


def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5, button: str = "left") -> dict:
    """
    Drag the mouse from start coordinates to end coordinates using pixel coordinates.
    
    Args:
        start_x (int): Starting X coordinate in pixels
        start_y (int): Starting Y coordinate in pixels
        end_x (int): Ending X coordinate in pixels
        end_y (int): Ending Y coordinate in pixels
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

from uuid import uuid4
import requests
from mcp.server.fastmcp import FastMCP, Image
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair

FASTAPI_URL = "http://localhost:8000"

key_pair = RSAKeyPair.generate()                 # genera par RSA
auth = BearerAuthProvider(                       # valida los JWT
    public_key=key_pair.public_key,
    issuer="https://auth.local",
    audience="BalatroGameMCP"
)

mcp = FastMCP(name="BalatroGameMCP", host="0.0.0.0", port=8001)

@mcp.tool(
    description="Click at a specific coordinate on the screen using relative coordinates (0-1).",
    required_scope="balatro.mouse"
)
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

@mcp.tool(
    description="Move the mouse cursor to a specific coordinate using relative coordinates (0-1).",
    required_scope="balatro.mouse"
)
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

@mcp.tool(
    description="Drag the mouse from start coordinates to end coordinates using relative coordinates (0-1).",
    required_scope="balatro.mouse"
)
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

@mcp.tool(
    description="Press a sequence of buttons to control the Balatro game. These buttons are from Xbox controller: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT. Example: 'A B LEFT RB'",
    required_scope="balatro.gamepad"
)
def press_buttons(sequence: str) -> dict:
    """
    Press a sequence of buttons to control the Balatro game.

    Args:
        sequence (str): A string with the sequence of buttons to press, separated by spaces.
                        Each button must be one of: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT.
    
    Returns:
        dict: A dictionary indicating if the action worked correctly.
              If there is an error, it will be explained.
    """
    try:
        step_id = str(uuid4())
        
        payload = {
            "step_id": step_id,
            "buttons": sequence,
            "duration": 0.1
        }

        response = requests.post(f"{FASTAPI_URL}/gamepad/buttons", json=payload, timeout=10)
        
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

@mcp.tool(
    description="Get a screenshot of the current state of the Balatro game.",
    required_scope="balatro.gamepad"
)
def get_screen() -> Image:
    """
    Get a screenshot of the current state of the Balatro game.
    
    Returns:
        ImageContent: A screenshot of the game showing the current state.
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/screenshot", timeout=10)

        if response.status_code != 200:
            raise RuntimeError(f"Screenshot backend error: HTTP {response.status_code} - {response.text}")

        return Image(data=response.content, format="png")
        
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to get screenshot: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error getting screenshot: {str(e)}")
    
@mcp.tool(
    description="Get the current mouse position in both absolute and relative coordinates.",
    required_scope="balatro.mouse"
)
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

@mcp.tool(
    description="Get a screenshot with cursor position visible.",
    required_scope="balatro.mouse"
)
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


if __name__ == "__main__":
    mcp.run(transport="streamable-http", mount_path="/mcp")
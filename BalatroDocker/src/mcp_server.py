from fastmcp import FastMCP
from uuid import uuid4
import requests
from fastmcp.utilities.types import Image, ImageContent

FASTAPI_URL = "http://localhost:8000"
mcp = FastMCP(name="BalatroGameMCP")

@mcp.tool(description="Press a sequence of buttons to control the Balatro game. These buttons are from Xbox controller: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT. Example: 'A B LEFT RB'")
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

@mcp.tool(description="Get a screenshot of the current state of the Balatro game.")
def get_screen() -> ImageContent:
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

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001, path="/mcp")
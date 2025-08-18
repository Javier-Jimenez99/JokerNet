"""
Standalone MCP (Model Context Protocol) Server for Balatro game control.

This server provides MCP tools for gamepad control and mouse interaction
with the Balatro game. Runs independently from the REST API.
"""

# Core system initialization
from api.utils.system import wait_for_x11, ensure_xauth

# Initialize X11 system first
print("Initializing X11 for MCP server...")
wait_for_x11()
ensure_xauth()
print("X11 initialization complete for MCP server")

from fastmcp import FastMCP
import uvicorn
import contextlib
from fastapi import FastAPI

# MCP tools
from mcp_server.tools.gamepad_tools import (
    press_buttons as _press_buttons,
    get_screen as _get_screen,
)
from mcp_server.tools.mouse_tools import (
    mouse_click as _mouse_click,
    mouse_drag as _mouse_drag, 
    locate_element as _locate_element,
    get_screen_with_cursor as _get_screen_with_cursor,
    get_screen_dimensions as _get_screen_dimensions,
)

# Initialize MCP server
gamepad_mcp = FastMCP(
    name="BalatroGamepadMCP",
)

# Gamepad Tools
@gamepad_mcp.tool()
def press_buttons(sequence: str) -> dict:
    """
    Press a sequence of buttons to control the Balatro game using Xbox controller layout.
    
    This function simulates pressing controller buttons in sequence to interact with the game.
    All button presses are executed immediately and sequentially.
    
    Parameters
    ----------
    sequence : str
        Space-separated string of button names to press in order.
        Valid buttons: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT.
        Example: 'A B LEFT RB' will press A, then B, then LEFT, then RB.
        
    Returns
    -------
    dict
        Dictionary containing the status of the button sequence execution.
        Keys include:
        - 'status': str, execution status ('success' or 'error')
        - 'buttons_pressed': list, buttons that were successfully pressed
        - 'message': str, descriptive message about the execution
    """
    return _press_buttons(sequence)

@gamepad_mcp.tool()
def get_screen():
    """
    Capture and return a screenshot of the current Balatro game state.
    
    This function takes a screenshot of the game window and returns it as base64 encoded data.
    Use this to analyze the current game state before making decisions.
        
    Returns
    -------
    dict
        Dictionary containing the screenshot data and metadata.
        Keys include:
        - 'image': str, base64 encoded PNG image data
        - 'width': int, screenshot width in pixels
        - 'height': int, screenshot height in pixels
        - 'timestamp': str, when the screenshot was taken
    """
    return _get_screen()

mouse_mcp = FastMCP(
    name="BalatroMouseMCP",
)

# Mouse Tools
# @mouse_mcp.tool()
# def locate_element(description: str) -> dict:
#     """
#     Locate UI elements on the screen using a brief text description and computer vision.
    
#     This function uses the AskUI PTA-1 model to detect UI elements and automatically calculates
#     optimal click positions. Always use this function before clicking to ensure accurate targeting.
    
#     Parameters
#     ----------
#     description : str
#         Brief, clear description of the UI element to locate.
#         Examples: "Select button", "Big Blind", "Run Info", "Options button", "Skip Blind"
#         Be specific but concise - focus on distinctive visual features.
        
#     Returns
#     -------
#     dict
#         Detection result with the following structure:
#         {
#             "status": "success" | "error",
#             "result": {
#                 "<OPEN_VOCABULARY_DETECTION>": {
#                     "bboxes": [],  # List of bounding boxes (if any): [[x1, y1, x2, y2], ...]
#                     "bboxes_labels": [],  # Labels for each bounding box
#                     "polygons": [[[x1, y1, x2, y2, x3, y3, x4, y4, ...]]],  # List of polygons
#                     "polygons_labels": ["Element Name"],  # Labels for each polygon
#                     "click_positions": [{"x": int, "y": int}]  # Ready-to-use click coordinates
#                 }
#             }
#         }
        
#         The click_positions field contains the calculated center points of detected elements,
#         ready for direct use with mouse_click(). Each position corresponds to the element
#         at the same index in polygons or bboxes.
        
#         If status is "error", the dict contains a "message" field with error details.
#     """
#     return _locate_element(description)

@mouse_mcp.tool()
def mouse_click(x: int, y: int) -> dict:
    f"""
    Click at a specific pixel coordinate on the screen.
    The resolution of the screenshot is {_get_screen_dimensions()}.

    Parameters
    ----------
    x : int
        X-coordinate in pixels from the left edge of the screen.
        Must be within screen bounds (0 to screen_width-1).
    y : int
        Y-coordinate in pixels from the top edge of the screen.
        Must be within screen bounds (0 to screen_height-1).
        
    Returns
    -------
    dict
        Click execution result with the following structure:
        {{
            "status": "success" | "error",
            "x": int,  # Actual x-coordinate clicked
            "y": int,  # Actual y-coordinate clicked
            "message": str  # Descriptive message about the click result
        }}
    """
    return _mouse_click(x, y)

@mouse_mcp.tool()
def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5, button: str = "left") -> dict:
    """
    Drag the mouse from start coordinates to end coordinates.
    
    Performs a mouse drag operation by pressing the mouse button at start coordinates,
    moving to end coordinates, and releasing the button. Use for dragging cards or UI elements.
    
    Parameters
    ----------
    start_x : int
        Starting x-coordinate in pixels from the left edge of the screen.
        Must be within screen bounds (0 to screen_width-1).
    start_y : int
        Starting y-coordinate in pixels from the top edge of the screen.
        Must be within screen bounds (0 to screen_height-1).
    end_x : int
        Ending x-coordinate in pixels from the left edge of the screen.
        Must be within screen bounds (0 to screen_width-1).
    end_y : int
        Ending y-coordinate in pixels from the top edge of the screen.
        Must be within screen bounds (0 to screen_height-1).
    duration : float, optional
        Duration of the drag operation in seconds. Default is 0.5.
        Longer duration for smoother drag, shorter for quick movements.
    button : str, optional
        Mouse button to use for dragging. Valid options: "left", "right", "middle".
        Default is "left".
        
    Returns
    -------
    dict
        Dictionary containing the drag execution result.
        Keys include:
        - 'status': str, execution status ('success' or 'error')
        - 'start_x': int, actual starting x-coordinate
        - 'start_y': int, actual starting y-coordinate
        - 'end_x': int, actual ending x-coordinate
        - 'end_y': int, actual ending y-coordinate
        - 'duration': float, actual duration of the drag
        - 'message': str, descriptive message about the execution
    """
    return _mouse_drag(start_x, start_y, end_x, end_y, duration, button)

@mouse_mcp.tool()
def get_screen():
    """
    Capture a screenshot with the current mouse cursor information.
        
    Returns
    -------
    dict
        Dictionary containing the screenshot with cursor and metadata.
        Keys include:
        - 'image': str, base64 encoded PNG image with cursor overlay
        - 'width': int, screenshot width in pixels
        - 'height': int, screenshot height in pixels
        - 'cursor_x': int, current cursor x-position in pixels
        - 'cursor_y': int, current cursor y-position in pixels
        - 'timestamp': str, when the screenshot was taken
    """
    return _get_screen()

def create_fastapi_app() -> FastAPI:
    # Create individual MCP apps
    gamepad_mcp_app = gamepad_mcp.http_app()
    mouse_mcp_app = mouse_mcp.http_app()

    # Create combined MCP application
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        async with gamepad_mcp_app.lifespan(app):
            async with mouse_mcp_app.lifespan(app):
                yield

    app = FastAPI(
        title="Balatro MCP Server",
        description="""
        MCP (Model Context Protocol) Server for Balatro game control.
        
        Provides AI agents with tools for:
        - Gamepad control
        - Mouse interaction
        - Screenshot capture
        """,
        version="1.0.0",
        lifespan=lifespan
    )

    # Mount the MCP servers
    app.mount("/gamepad", gamepad_mcp_app)
    app.mount("/mouse", mouse_mcp_app)

    # Health check for MCP server
    @app.get("/health")
    async def health_check():
        """MCP server health check."""
        return {
            "status": "healthy",
            "services": {
                "gamepad_mcp": "running",
                "mouse_mcp": "running"
            }
        }
    
    return app


# Main execution for standalone MCP server
if __name__ == "__main__":
    app = create_fastapi_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
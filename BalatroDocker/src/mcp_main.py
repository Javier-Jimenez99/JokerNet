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
@gamepad_mcp.tool(
    description="Press a sequence of buttons to control the Balatro game. These buttons are from Xbox controller: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT. Example: 'A B LEFT RB'.",
)
def press_buttons(sequence: str) -> dict:
    return _press_buttons(sequence)

@gamepad_mcp.tool(
    description="Get a screenshot of the current state of the Balatro game.",
)
def get_screen():
    return _get_screen()

mouse_mcp = FastMCP(
    name="BalatroMouseMCP",
)

# Get screen dimensions for dynamic descriptions
def get_screen_info_text():
    """Get screen dimension text for tool descriptions."""
    try:
        dims = _get_screen_dimensions()
        return f"Screen resolution: {dims['width']}x{dims['height']} pixels. "
    except:
        return "Screen resolution: Available via get_mouse_position. "

# Mouse Tools
# @mouse_mcp.tool(
#     description=f"Get the current mouse position in pixel coordinates. Also returns current screen dimensions.",
# )
# def get_mouse_position() -> dict:
#     return _get_mouse_position()

@mouse_mcp.tool(
    description=f"Locate an element on the screen by a brief description.",
)
def locate_element(description: str) -> dict:
    return _locate_element(description)

@mouse_mcp.tool(
    description=f"Click at a specific coordinate on the screen using pixel coordinates. {get_screen_info_text()}Use exact pixel coordinates for precise clicking.",
)
def mouse_click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
    return _mouse_click(x, y, button, clicks)

# @mouse_mcp.tool(
#     description=f"Move the mouse cursor to a specific coordinate using pixel coordinates. {get_screen_info_text()}Use exact pixel coordinates for precise movement.",
# )
# def mouse_move(x: int, y: int, duration: float = 0.0) -> dict:
#     return _mouse_move(x, y, duration)

@mouse_mcp.tool(
    description=f"Drag the mouse from start coordinates to end coordinates using pixel coordinates. {get_screen_info_text()}Use exact pixel coordinates for precise dragging.",
)
def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5, button: str = "left") -> dict:
    return _mouse_drag(start_x, start_y, end_x, end_y, duration, button)

@mouse_mcp.tool(
    description=f"Get a screenshot with cursor position visible. The cursor is a light green point inside a larger dark green circle, to make it more visible. Use this to see the current game state and plan your next mouse actions using pixel coordinates. {get_screen_info_text()}",
)
def get_screen_with_cursor():
    return _get_screen_with_cursor()

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
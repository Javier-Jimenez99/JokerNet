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
    get_screen as _get_screen
)
from mcp_server.tools.mouse_tools import (
    get_mouse_position as _get_mouse_position, 
    mouse_click as _mouse_click, 
    mouse_move as _mouse_move, 
    mouse_drag as _mouse_drag, 
    get_screen_with_cursor as _get_screen_with_cursor
)

# Initialize MCP server
gamepad_mcp = FastMCP(
    name="BalatroGamepadMCP",
)

# Gamepad Tools
@gamepad_mcp.tool(
    description="Press a sequence of buttons to control the Balatro game. These buttons are from Xbox controller: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT. Example: 'A B LEFT RB'",
)
def press_buttons(sequence: str) -> dict:
    """Press a sequence of buttons to control the Balatro game."""
    return _press_buttons(sequence)

@gamepad_mcp.tool(
    description="Get a screenshot of the current state of the Balatro game.",
)
def get_screen():
    """Get a screenshot of the current state of the Balatro game."""
    return _get_screen()

mouse_mcp = FastMCP(
    name="BalatroMouseMCP",
)

# Mouse Tools
@mouse_mcp.tool(
    description="Get the current mouse position in both absolute and relative coordinates.",
)
def get_mouse_position() -> dict:
    """Get the current mouse position in both absolute and relative coordinates."""
    return _get_mouse_position()

@mouse_mcp.tool(
    description="Click at a specific coordinate on the screen using relative coordinates (0-1).",
)
def mouse_click(x: float, y: float, button: str = "left", clicks: int = 1) -> dict:
    """Click at a specific coordinate on the screen using relative coordinates."""
    return _mouse_click(x, y, button, clicks)

@mouse_mcp.tool(
    description="Move the mouse cursor to a specific coordinate using relative coordinates (0-1).",
)
def mouse_move(x: float, y: float, duration: float = 0.0) -> dict:
    """Move the mouse cursor to a specific coordinate using relative coordinates."""
    return _mouse_move(x, y, duration)

@mouse_mcp.tool(
    description="Drag the mouse from start coordinates to end coordinates using relative coordinates (0-1).",
)
def mouse_drag(start_x: float, start_y: float, end_x: float, end_y: float, duration: float = 0.5, button: str = "left") -> dict:
    """Drag the mouse from start coordinates to end coordinates using relative coordinates."""
    return _mouse_drag(start_x, start_y, end_x, end_y, duration, button)

@mouse_mcp.tool(
    description="Get a screenshot with cursor position visible.",
)
def get_screen_with_cursor():
    """Get a screenshot with the current mouse cursor position highlighted."""
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
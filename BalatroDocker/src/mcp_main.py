"""
MCP (Model Context Protocol) Server for Balatro game control.

This server provides MCP tools for gamepad control and mouse interaction
with the Balatro game through the FastAPI backend.
"""
from fastmcp import FastMCP

# MCP tools
from mcp_server.tools.gamepad_tools import press_buttons, get_screen
from mcp_server.tools.mouse_tools import (
    get_mouse_position, 
    mouse_click, 
    mouse_move, 
    mouse_drag, 
    get_screen_with_cursor
)

# Initialize MCP server
gamepad_mcp = FastMCP(
    name="BalatroGamepadMCP",
)

mouse_mcp = FastMCP(
    name="BalatroMouseMCP",
)

# Gamepad Tools
@gamepad_mcp.tool(
    description="Press a sequence of buttons to control the Balatro game. These buttons are from Xbox controller: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT. Example: 'A B LEFT RB'",
)
def press_buttons_tool(sequence: str) -> dict:
    """Press a sequence of buttons to control the Balatro game."""
    return press_buttons(sequence)

@gamepad_mcp.tool(
    description="Get a screenshot of the current state of the Balatro game.",
)
def get_screen_tool():
    """Get a screenshot of the current state of the Balatro game."""
    return get_screen()

# Mouse Tools
@mouse_mcp.tool(
    description="Get the current mouse position in both absolute and relative coordinates.",
    tags=["balatro.mouse"]
)
def get_mouse_position_tool() -> dict:
    """Get the current mouse position in both absolute and relative coordinates."""
    return get_mouse_position()

@mouse_mcp.tool(
    description="Click at a specific coordinate on the screen using relative coordinates (0-1).",
    tags=["balatro.mouse"]
)
def mouse_click_tool(x: float, y: float, button: str = "left", clicks: int = 1) -> dict:
    """Click at a specific coordinate on the screen using relative coordinates."""
    return mouse_click(x, y, button, clicks)

@mouse_mcp.tool(
    description="Move the mouse cursor to a specific coordinate using relative coordinates (0-1).",
    tags=["balatro.mouse"]
)
def mouse_move_tool(x: float, y: float, duration: float = 0.0) -> dict:
    """Move the mouse cursor to a specific coordinate using relative coordinates."""
    return mouse_move(x, y, duration)

@mouse_mcp.tool(
    description="Drag the mouse from start coordinates to end coordinates using relative coordinates (0-1).",
    tags=["balatro.mouse"]
)
def mouse_drag_tool(start_x: float, start_y: float, end_x: float, end_y: float, duration: float = 0.5, button: str = "left") -> dict:
    """Drag the mouse from start coordinates to end coordinates using relative coordinates."""
    return mouse_drag(start_x, start_y, end_x, end_y, duration, button)

@mouse_mcp.tool(
    description="Get a screenshot with cursor position visible.",
    tags=["balatro.mouse"]
)
def get_screen_with_cursor_tool():
    """Get a screenshot with the current mouse cursor position highlighted."""
    return get_screen_with_cursor()

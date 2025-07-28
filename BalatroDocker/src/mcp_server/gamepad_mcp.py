"""
MCP Server for Balatro gamepad control.

This server provides MCP tools specifically for gamepad interaction
with the Balatro game through the FastAPI backend.
"""
from fastmcp import FastMCP

# Import gamepad tools
from mcp_server.tools.gamepad_tools import press_buttons, get_screen

# Initialize gamepad MCP server
mcp = FastMCP(
    name="BalatroGamepadMCP",
    include_tags=["balatro.gamepad"],
)

# Gamepad Tools
@mcp.tool(
    description="Press a sequence of buttons to control the Balatro game. These buttons are from Xbox controller: A, B, X, Y, LEFT, RIGHT, UP, DOWN, START, SELECT, RB, RT, LB, LT. Example: 'A B LEFT RB'",
    tags=["balatro.gamepad"]
)
def press_buttons_tool(sequence: str) -> dict:
    """Press a sequence of buttons to control the Balatro game."""
    return press_buttons(sequence)

@mcp.tool(
    description="Get a screenshot of the current state of the Balatro game.",
    tags=["balatro.gamepad"]
)
def get_screen_tool():
    """Get a screenshot of the current state of the Balatro game."""
    return get_screen()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", mount_path="/mcp/gamepad")

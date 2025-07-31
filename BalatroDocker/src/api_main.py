"""
Pure REST API server for Balatro game control.

This server provides REST API endpoints for controlling the Balatro game.
No MCP integration - only HTTP REST endpoints.
"""

# Core system initialization
from api.utils.system import wait_for_x11, ensure_xauth

# Initialize X11 system first
print("Initializing X11 for API server...")
wait_for_x11()
ensure_xauth()
print("X11 initialization complete for API server")

# API controllers (import after X11 initialization)
from api.controllers import (
    game_controller,
    gamepad_controller,
    mouse_controller,
    screenshot_controller
)

# API models
from api.models.requests import (
    GamepadButtonsRequest,
    MouseClickRequest,
    MouseMoveRequest,
    MouseDragRequest,
    AutoStartRequest
)

import time
import uvicorn
from fastapi import FastAPI

def create_fastapi_app():

    # Create main application
    app = FastAPI(
        title="Balatro Game Control REST API",
        description="""
        REST API for controlling Balatro game through HTTP endpoints.
        
        Uses relative coordinates (0-1) where 0 represents top/left edge and 1 represents bottom/right edge.
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Game Management Endpoints
    @app.post("/start_balatro", tags=["Game Management"], summary="Start Balatro Game")
    async def start_balatro():
        """Start Balatro with mods using Lovely."""
        return await game_controller.start_balatro()

    @app.post("/stop_balatro", tags=["Game Management"], summary="Stop Balatro Game")
    async def stop_balatro():
        """Stop Balatro game."""
        return await game_controller.stop_balatro()

    @app.post("/auto_start", tags=["Game Management"], summary="Configure Auto-Start")
    async def auto_start_game(request: AutoStartRequest):
        """Configure and trigger auto-start with specific deck, stake, and seed."""
        return await game_controller.auto_start_game(request)

    @app.get("/mod_status", tags=["Game Management"], summary="Get Mod Status")
    async def get_mod_status():
        """Get current mod status."""
        return await game_controller.get_mod_status()

    # Gamepad Control Endpoints
    @app.post("/gamepad/buttons", tags=["Gamepad Control"], summary="Press Gamepad Buttons")
    async def press_gamepad_button(request: GamepadButtonsRequest):
        """Press one or more gamepad buttons. Valid buttons: A, B, X, Y, LB, RB, LT, RT, START, BACK, SELECT, UP, DOWN, LEFT, RIGHT"""
        return await gamepad_controller.press_gamepad_button(request)

    # Mouse Control Endpoints
    @app.post("/mouse/click", tags=["Mouse Control"], summary="Click at Coordinates")
    async def mouse_click(request: MouseClickRequest):
        """Click at specific coordinates using relative positioning (0-1)."""
        return await mouse_controller.mouse_click(request)

    @app.post("/mouse/move", tags=["Mouse Control"], summary="Move Mouse Cursor")
    async def mouse_move(request: MouseMoveRequest):
        """Move mouse cursor to specific coordinates using relative positioning (0-1)."""
        return await mouse_controller.mouse_move(request)

    @app.post("/mouse/drag", tags=["Mouse Control"], summary="Drag Mouse")
    async def mouse_drag(request: MouseDragRequest):
        """Drag from start coordinates to end coordinates using relative positioning (0-1)."""
        return await mouse_controller.mouse_drag(request)

    @app.get("/mouse/position", tags=["Mouse Control"], summary="Get Mouse Position")
    async def get_mouse_position():
        """Get current mouse position in both absolute and relative coordinates."""
        return await mouse_controller.get_mouse_position()

    # Screenshot Endpoints
    @app.get("/screenshot", tags=["Screenshot"], summary="Take Screenshot")
    async def get_screenshot():
        """Take a screenshot of the current screen."""
        return await screenshot_controller.get_screenshot()

    @app.get("/screenshot_with_cursor", tags=["Screenshot"], summary="Take Screenshot with Cursor")
    async def get_screenshot_with_cursor():
        """Take screenshot with visible cursor position marked."""
        return await screenshot_controller.get_screenshot_with_cursor()

    # Enhanced Health Check Endpoint
    @app.get("/health", tags=["System"], summary="Health Check")
    async def health_check():
        """API health check endpoint."""
        return {
            "status": "healthy", 
            "timestamp": time.time(),
            "services": {
                "rest_api": "running"
            }
        }
    
    return app

# Main execution for standalone API server
if __name__ == "__main__":
    app = create_fastapi_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
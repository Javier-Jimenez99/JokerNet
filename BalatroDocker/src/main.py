"""
Main FastAPI application for Balatro game control with integrated MCP server.

This is the main entry point that combines:
- REST API for direct game control (from api_main)
- MCP server for gamepad and mouse control (from mcp_main)

All under a single FastAPI application.
"""

# Core system initialization
from api.utils.system import wait_for_x11, ensure_xauth

# Initialize X11 system first
print("Initializing X11...")
wait_for_x11()
ensure_xauth()
print("X11 initialization complete")

# Initialize MCP server
from mcp_main import gamepad_mcp, mouse_mcp
from api_main import create_fastapi_app
import contextlib
from fastapi import FastAPI
import uvicorn

import contextlib

gamepad_mcp_app = gamepad_mcp.http_app()
mouse_mcp_app = mouse_mcp.http_app()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with gamepad_mcp_app.lifespan(app):
        async with mouse_mcp_app.lifespan(app):
            yield

app = create_fastapi_app(lifespan=lifespan)

# Mount the MCP server
app.mount("/gamepad", gamepad_mcp_app)
app.mount("/mouse", mouse_mcp_app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

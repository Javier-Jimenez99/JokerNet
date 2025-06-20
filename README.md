# Balatro Gamepad Controller

Minimal API for controlling Balatro with virtual gamepad inputs in Docker.

## Features

- **Virtual Gamepad Control**: Send gamepad button presses to Balatro running in Docker
- **Multiple Input Fallbacks**: Native uinput → vgamepad → keyboard fallback for reliability
- **Window Focus Management**: Automatically focuses Balatro window for input delivery
- **Event Logging**: Receive events from BalatroLogger mod
- **Minimal Setup**: Clean, production-ready configuration

## Quick Start

1. **Build and run**:
   ```bash
   docker compose up --build
   ```

2. **Send gamepad inputs**:
   ```bash
   # Press A button
   curl -X POST "http://localhost:8000/gamepad/button" \
        -H "Content-Type: application/json" \
        -d '{"button": "A", "duration": 0.1}'
   
   # Press D-pad up
   curl -X POST "http://localhost:8000/gamepad/button" \
        -H "Content-Type: application/json" \
        -d '{"button": "DPAD_UP"}'
   ```

3. **Start/stop Balatro**:
   ```bash
   # Start game
   curl -X POST "http://localhost:8000/start_balatro"
   
   # Stop game
   curl -X POST "http://localhost:8000/stop_balatro"
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/gamepad/button` | POST | Press gamepad button |
| `/start_balatro` | POST | Start Balatro with mods |
| `/stop_balatro` | POST | Stop Balatro |
| `/logger/status` | GET | Logger events status |
| `/status` | GET | System status |
| `/health` | GET | Health check |

## Supported Buttons

- **Face buttons**: A, B, X, Y
- **Shoulder buttons**: LB, RB  
- **Menu buttons**: START, BACK
- **D-pad**: DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT

## Input Fallback System

1. **Native uinput**: Creates Xbox gamepad device directly
2. **vgamepad**: Virtual gamepad library fallback
3. **Keyboard**: Final fallback using keyboard keys

## Requirements

- Docker with privileged mode
- `/dev/uinput` and `/dev/input` device access
- uinput kernel module loaded

## Configuration

The system auto-configures paths and mods. Key environment variables:

- `DISPLAY=:1`: X11 display for the containerized environment
- `LOVELY_MOD_DIR`: Mods directory for Lovely mod loader
- `LD_PRELOAD`: Preload Lovely for mod support

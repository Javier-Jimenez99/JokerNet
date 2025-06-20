# Balatro Gamepad Controller

Minimal API for controlling Balatro with virtual gamepad inputs in Docker.

## Features

- **Virtual Gamepad Control**: Send gamepad button presses to Balatro running in Docker
- **Native uinput Integration**: Direct Xbox gamepad device emulation through Linux kernel
- **Window Focus Management**: Automatically focuses Balatro window for input delivery
- **Minimal Setup**: Clean, production-ready configuration

## Prerequisites (Host Setup)

**IMPORTANT**: Before running the container, execute these commands on the host system:

```bash
# Load uinput kernel module
sudo modprobe uinput

# Set permissions for uinput device
sudo chmod 666 /dev/uinput
```

These commands are required because:
- Containers share the host kernel and cannot load kernel modules themselves
- The `/dev/uinput` device is needed for virtual gamepad functionality
- Proper permissions are required for the container to access the device

## Quick Start

1. **Setup host prerequisites** (see above)

2. **Build and run**:
   ```bash
   docker compose up --build
   ```

   Or run manually with required privileges:
   ```bash
   docker run --privileged \
     --device=/dev/uinput \
     -v /dev:/dev \
     -p 8000:8000 \
     your-balatro-image
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
| `/health` | GET | Health check |

## Supported Buttons

- **Face buttons**: A, B, X, Y
- **Shoulder buttons**: LB, RB  
- **Menu buttons**: START, BACK
- **D-pad**: DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT

## Input System

The controller uses **native uinput exclusively** to create a virtual Xbox gamepad device directly through the Linux kernel. This provides the most reliable and authentic gamepad input for Balatro.

**No fallbacks**: The system requires a working uinput device - if uinput fails, gamepad input will not work.

## Requirements

- Docker with privileged mode and device access
- Host system with uinput kernel module loaded
- `/dev/uinput` device access from container

## Configuration

The system auto-configures paths and mods. Key environment variables:

- `DISPLAY=:1`: X11 display for the containerized environment
- `LOVELY_MOD_DIR`: Mods directory for Lovely mod loader
- `LD_PRELOAD`: Preload Lovely for mod support

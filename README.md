# Balatro Auto-Start Controller

Minimal API for controlling Balatro with virtual gamepad inputs and auto-starting games in Docker.

## Features

- **Virtual Gamepad Control**: Send gamepad button presses to Balatro running in Docker
- **Auto-Start Games**: Automatically start games with specific deck/stake configuration
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

4. **Take screenshot**:
   ```bash
   # Get screenshot (returns PNG image)
   curl "http://localhost:8000/screenshot" > screenshot.png
   ```

5. **Auto-start game with configuration**:
   ```bash
   # Iniciar con configuración básica (mazo y apuesta predeterminados)
   curl -X POST "http://localhost:8000/auto_start" \
        -H "Content-Type: application/json" \
        -d '{"auto_start": true}'
   
   # Iniciar con mazo específico
   curl -X POST "http://localhost:8000/auto_start" \
        -H "Content-Type: application/json" \
        -d '{"auto_start": true, "deck": "b_blue"}'
   
   # Iniciar con configuración completa
   curl -X POST "http://localhost:8000/auto_start" \
        -H "Content-Type: application/json" \
        -d '{"auto_start": true, "deck": "b_magic", "stake": 5, "seed": "MYSTICAL2024"}'
   
   # Iniciar con semilla aleatoria
   curl -X POST "http://localhost:8000/auto_start" \
        -H "Content-Type: application/json" \
        -d '{"auto_start": true, "deck": "b_nebula", "stake": 2, "seed": "random"}'
   
   # Verificar estado del mod
   curl "http://localhost:8000/mod_status"
   ```

## Auto-Start Configuration Options

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `auto_start` | boolean | ✅ | Activar el auto-inicio |
| `deck` | string | ❌ | ID del mazo (ej: "b_red", "b_blue", "b_magic") |
| `stake` | number | ❌ | Nivel de apuesta (1-8, donde 1=Blanca, 8=Dorada) |
| `seed` | string | ❌ | Semilla personalizada o "random" |

### Mazos Disponibles
- `b_red` - Mazo Rojo (predeterminado)
- `b_blue` - Mazo Azul
- `b_yellow` - Mazo Amarillo
- `b_green` - Mazo Verde
- `b_black` - Mazo Negro
- `b_magic` - Mazo Mágico
- `b_nebula` - Mazo Nebulosa
- `b_ghost` - Mazo Fantasma
- `b_abandoned` - Mazo Abandonado
- `b_checkered` - Mazo Ajedrezado
- `b_zodiac` - Mazo Zodiaco
- `b_painted` - Mazo Pintado
- `b_anaglyph` - Mazo Anaglifo
- `b_plasma` - Mazo Plasma
- `b_erratic` - Mazo Errático

**Nota**: Solo funcionan mazos desbloqueados en el juego.

### Apuestas (Stakes)
1. **Apuesta Blanca** (más fácil)
2. **Apuesta Roja**
3. **Apuesta Verde**
4. **Apuesta Negra**
5. **Apuesta Azul**
6. **Apuesta Púrpura**
7. **Apuesta Naranja**
8. **Apuesta Dorada** (más difícil)

**Nota**: Solo funcionan apuestas desbloqueadas en el juego.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/gamepad/button` | POST | Press gamepad button |
| `/start_balatro` | POST | Start Balatro with mods |
| `/stop_balatro` | POST | Stop Balatro |
| `/auto_start` | POST | Auto-start game with config |
| `/mod_status` | GET | Get mod status |
| `/screenshot` | GET | Take a screenshot of the game |
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

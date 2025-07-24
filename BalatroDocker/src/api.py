import os
import subprocess

def wait_for_x11():
    """Wait for X11 to be available"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ['xdpyinfo', '-display', ':0'], 
                capture_output=True, 
                timeout=5
            )
            if result.returncode == 0:
                print("X11 server is ready!")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print(f"Waiting for X11 server... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(1)
    
    print("Warning: X11 server not available after 30 seconds")
    return False

def ensure_xauth():
    """Ensure X11 authorization is set up"""
    try:
        if not os.path.exists('/root/.Xauthority'):
            print("Creating X11 authority file...")
            open('/root/.Xauthority', 'a').close()
            subprocess.run(['xauth', 'add', ':0', '.', '$(xxd -l 16 -p /dev/urandom)'],
                         capture_output=True)
        return True
    except Exception as e:
        print(f"Warning: Could not set up X11 auth: {e}")
        return False

def relative_to_absolute(rel_x: float, rel_y: float):
    """Convert relative coordinates (0-1) to absolute screen coordinates"""
    screen_width, screen_height = pyautogui.size()
    
    # Clamp values to 0-1 range
    rel_x = max(0.0, min(1.0, rel_x))
    rel_y = max(0.0, min(1.0, rel_y))
    
    # Convert to absolute coordinates
    abs_x = int(rel_x * screen_width)
    abs_y = int(rel_y * screen_height)
    
    return abs_x, abs_y
    
# Initialize X11 on startup
print("Initializing X11...")
wait_for_x11()
ensure_xauth()
print("X11 initialization complete")

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageColor
import io
import time
import pyautogui
from typing import Optional
from pydantic import BaseModel
import uinput

ACTIONS_DONE = {}

def draw_point(image: Image.Image, point: list, color=None):
    if isinstance(color, str):
        try:
            color = ImageColor.getrgb(color)
            color = color + (128,)  
        except ValueError:
            color = (255, 0, 0, 128)  
    else:
        color = (255, 0, 0, 128)  

    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    radius = min(image.size) * 0.05
    x, y = point

    overlay_draw.ellipse(
        [(x - radius, y - radius), (x + radius, y + radius)],
        fill=color
    )
    
    center_radius = radius * 0.1
    overlay_draw.ellipse(
        [(x - center_radius, y - center_radius), 
         (x + center_radius, y + center_radius)],
        fill=(0, 255, 0, 255)
    )

    image = image.convert('RGBA')
    combined = Image.alpha_composite(image, overlay)

    return combined.convert('RGB')

class BalatroGamepadController:
    def __init__(self):
        self.native_gamepad = None
        self.balatro_window_id = None
        self._init_controllers()
    
    def _init_controllers(self):
        """Initialize native uinput gamepad"""
        try:
            self.native_gamepad = self._create_native_gamepad()
        except Exception as e:
            print(f"Failed to initialize native gamepad: {e}")
            self.native_gamepad = None
    
    def _create_native_gamepad(self):
        """Create native gamepad using uinput"""        
        events = [
            # Face buttons
            uinput.BTN_A, uinput.BTN_B, uinput.BTN_X, uinput.BTN_Y,
            # Shoulder buttons  
            uinput.BTN_TL, uinput.BTN_TR, uinput.ABS_Z + (0, 255, 0, 0),  # LT
            uinput.ABS_RZ + (0, 255, 0, 0),  # RT
            # Menu buttons
            uinput.BTN_SELECT, uinput.BTN_START,
            # D-pad
            uinput.ABS_HAT0X + (-1, 1, 0, 0),
            uinput.ABS_HAT0Y + (-1, 1, 0, 0),
            # Analog sticks
            uinput.ABS_X + (-32768, 32767, 0, 0),
            uinput.ABS_Y + (-32768, 32767, 0, 0), 
            uinput.ABS_RX + (-32768, 32767, 0, 0),
            uinput.ABS_RY + (-32768, 32767, 0, 0),
        ]
        
        device = uinput.Device(
            events,
            name="Microsoft X-Box One S pad",
            bustype=uinput.BUS_USB if hasattr(uinput, 'BUS_USB') else 0x03,
            vendor=0x045e,
            product=0x02ea,
            version=0x0408
        )
        
        # Reset to neutral
        device.emit(uinput.ABS_X, 0)
        device.emit(uinput.ABS_Y, 0)
        device.emit(uinput.ABS_RX, 0)
        device.emit(uinput.ABS_RY, 0)
        device.emit(uinput.ABS_HAT0X, 0)
        device.emit(uinput.ABS_HAT0Y, 0)
        device.emit(uinput.ABS_Z, 0)
        device.emit(uinput.ABS_RZ, 0)
        device.syn()
        
        return device
    
    def find_balatro_window(self):
        """Find Balatro window using wmctrl"""
        try:
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                return None
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'balatro' in line.lower() or 'love' in line.lower():
                    window_id = line.split()[0]
                    self.balatro_window_id = window_id
                    return window_id
            
            return None
            
        except Exception:
            return None
    
    def focus_balatro_window(self):
        """Focus Balatro window"""
        try:
            if not self.balatro_window_id:
                self.find_balatro_window()
            
            if self.balatro_window_id:
                result = subprocess.run(['wmctrl', '-i', '-a', self.balatro_window_id], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    time.sleep(0.1)
                    return True
            
            return False
                
        except Exception:
            return False
    
    def press_button(self, button_name: str, duration: float = 0.1):
        """Press gamepad button using native uinput"""
        
        if not self.native_gamepad:
            return {"status": "error", "message": "Native gamepad not available"}
        
        return self._press_button_native(button_name, duration)
    
    def _press_button_native(self, button_name: str, duration: float):
        """Press button with native gamepad"""
        try:            
            button_map = {
                'A': uinput.BTN_A,
                'B': uinput.BTN_B,
                'X': uinput.BTN_X,
                'Y': uinput.BTN_Y,
                'LB': uinput.BTN_TL,
                'RB': uinput.BTN_TR,
                'LT': uinput.ABS_Z,
                'RT': uinput.ABS_RZ,
                'START': uinput.BTN_START,
                'BACK': uinput.BTN_SELECT,
                'SELECT': uinput.BTN_SELECT,
            }
            
            dpad_map = {
                'UP': (uinput.ABS_HAT0Y, -1),
                'DOWN': (uinput.ABS_HAT0Y, 1),
                'LEFT': (uinput.ABS_HAT0X, -1),
                'RIGHT': (uinput.ABS_HAT0X, 1),
            }
            
            button_name = button_name.upper()
            self.focus_balatro_window()
            
            if button_name in button_map:
                button = button_map[button_name]
                self.native_gamepad.emit(button, 1)
                self.native_gamepad.syn()
                time.sleep(duration)
                self.native_gamepad.emit(button, 0)
                self.native_gamepad.syn()
                
            elif button_name in dpad_map:
                axis, value = dpad_map[button_name]
                self.native_gamepad.emit(axis, value)
                self.native_gamepad.syn()
                time.sleep(duration)
                self.native_gamepad.emit(axis, 0)
                self.native_gamepad.syn()
                
            else:
                return {"status": "error", "message": f"Button '{button_name}' not recognized"}
            
            return {
                "status": "success",
                "message": f"Button {button_name} pressed (native)",
                "method": "native_gamepad"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Native gamepad error: {e}"}
# Load configuration from file
def load_config():
    config = {}
    config_file = "/etc/app/paths.env"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = os.path.expandvars(value.strip('"'))
                    config[key] = value
    
    # Auto-derive paths
    steam_root = config.get('STEAM_ROOT', '/root/.local/share/Steam')
    user_data_dir = config.get('USER_DATA_DIR', '/root/.local/share/Balatro')
    lovely_install_dir = '/opt/lovely'
    balatro_love_dir = '/opt/balatro-love'
    
    config['BALATRO_STEAM_DIR'] = f"{steam_root}/steamapps/common/Balatro"
    config['BALATRO_LOVE_DIR'] = balatro_love_dir
    config['LOVELY_MODS_DIR'] = f"{user_data_dir}/Mods"
    config['LOVELY_INSTALL_DIR'] = lovely_install_dir
    config['BALATRO_CMD'] = 'love .'
    config['LOVELY_PRELOAD'] = f"{lovely_install_dir}/liblovely.so"
    
    return config

# Global configuration
CONFIG = load_config()
LOVELY_MODS_DIR = CONFIG.get('LOVELY_MODS_DIR', '/root/.local/share/Balatro/Mods')
BALATRO_CMD = CONFIG.get('BALATRO_CMD', 'love .')
BALATRO_LOVE_DIR = CONFIG.get('BALATRO_LOVE_DIR', '/opt/balatro-love')
LOVELY_PRELOAD = CONFIG.get('LOVELY_PRELOAD', '/opt/lovely/liblovely.so')

# API Models
class GamepadButtonsRequest(BaseModel):
    buttons: str
    step_id: Optional[str] = None
    duration: Optional[float] = 0.1

class MouseClickRequest(BaseModel):
    x: float  # Relative coordinate (0-1)
    y: float  # Relative coordinate (0-1)
    button: str = "left"
    clicks: int = 1

class MouseMoveRequest(BaseModel):
    x: float  # Relative coordinate (0-1)
    y: float  # Relative coordinate (0-1)
    duration: float = 0.0

class MouseDragRequest(BaseModel):
    start_x: float  # Relative coordinate (0-1)
    start_y: float  # Relative coordinate (0-1)
    end_x: float    # Relative coordinate (0-1)
    end_y: float    # Relative coordinate (0-1)
    duration: float = 0.5
    button: str = "left"

class AutoStartRequest(BaseModel):
    deck: Optional[str] = "b_red"
    stake: Optional[int] = 1
    seed: Optional[str] = None

# Global state
balatro_running = False

balatro_process: Optional[subprocess.Popen] = None
gamepad_controller = BalatroGamepadController()

app = FastAPI(
    title="Balatro Minimal API",
    description="Minimal API for Balatro gamepad control",
    version="1.0.0"
)

@app.post("/start_balatro")
async def start_balatro():
    """Start Balatro with mods using Lovely"""
    global balatro_process
    
    try:
        if balatro_process and balatro_process.poll() is None:
            return {
                "status": "already_running",
                "pid": balatro_process.pid
            }
        
        cmd = BALATRO_CMD.split()
        
        env = dict(os.environ, 
                  DISPLAY=":0", 
                  LD_PRELOAD=LOVELY_PRELOAD,
                  LOVELY_MOD_DIR=LOVELY_MODS_DIR)
        
        if not os.path.exists(LOVELY_MODS_DIR):
            os.makedirs(LOVELY_MODS_DIR, exist_ok=True)
        
        balatro_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=BALATRO_LOVE_DIR
        )
        
        global balatro_running
        balatro_running = True
        
        return {
            "status": "started",
            "pid": balatro_process.pid
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting Balatro: {e}")

@app.post("/stop_balatro")
async def stop_balatro():
    """Stop Balatro"""
    global balatro_process
    
    try:
        if not balatro_process:
            return {"status": "not_running"}
        
        if balatro_process.poll() is not None:
            return {"status": "already_stopped"}
        
        balatro_process.terminate()
        try:
            balatro_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            balatro_process.kill()
            balatro_process.wait()
        
        global balatro_running
        balatro_running = False
        balatro_process = None
        
        return {"status": "stopped"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping Balatro: {e}")

@app.post("/gamepad/buttons")
async def press_gamepad_button(request: GamepadButtonsRequest):
    """Press gamepad button"""
    global gamepad_controller

    buttons = request.buttons.split()
    if not buttons:
        raise HTTPException(status_code=400, detail="No buttons specified")
    
    result = None
    success = True

    for button in buttons:
        button = button.strip().upper()
        if button not in [
            'A', 'B', 'X', 'Y', 'LB', 'RB', 'LT', 'RT',
            'START', 'BACK', 'SELECT', 'UP', 'DOWN', 'LEFT', 'RIGHT'
        ]:
            raise HTTPException(status_code=400, detail=f"Invalid button: {button}")
        
        result = gamepad_controller.press_button(button, request.duration)
        
        time.sleep(1) # Wait for 1 second between button presses
    
        if result["status"] == "error":
            success = False
            break
            
        
    # Store action in global state
    if request.step_id:
        ACTIONS_DONE[request.step_id] = {
            "buttons": buttons,
            "timestamp": time.time(),
            "success": success,
        }

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "status": "success",
        "message": f"{buttons} pressed",
    }

@app.post("/mouse/click")
async def mouse_click(request: MouseClickRequest):
    """Click at specific coordinates (relative 0-1)"""
    try:
        # Convert relative coordinates to absolute
        abs_x, abs_y = relative_to_absolute(request.x, request.y)
        
        pyautogui.click(abs_x, abs_y, clicks=request.clicks, button=request.button)
        return {
            "status": "success",
            "message": f"Clicked at relative ({request.x:.3f}, {request.y:.3f}) -> absolute ({abs_x}, {abs_y}) with {request.button} button {request.clicks} time(s)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to click: {str(e)}")

@app.post("/mouse/move")
async def mouse_move(request: MouseMoveRequest):
    """Move mouse cursor to specific coordinates (relative 0-1)"""
    try:
        # Convert relative coordinates to absolute
        abs_x, abs_y = relative_to_absolute(request.x, request.y)
        
        pyautogui.moveTo(abs_x, abs_y, duration=request.duration)
        return {
            "status": "success",
            "message": f"Moved mouse to relative ({request.x:.3f}, {request.y:.3f}) -> absolute ({abs_x}, {abs_y})"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move mouse: {str(e)}")

@app.post("/mouse/drag")
async def mouse_drag(request: MouseDragRequest):
    """Drag from start coordinates to end coordinates (relative 0-1)"""
    try:
        # Convert relative coordinates to absolute
        abs_start_x, abs_start_y = relative_to_absolute(request.start_x, request.start_y)
        abs_end_x, abs_end_y = relative_to_absolute(request.end_x, request.end_y)
        
        pyautogui.drag(
            abs_end_x - abs_start_x,
            abs_end_y - abs_start_y,
            duration=request.duration,
            button=request.button,
            start=(abs_start_x, abs_start_y)
        )
        return {
            "status": "success",
            "message": f"Dragged from relative ({request.start_x:.3f}, {request.start_y:.3f}) -> absolute ({abs_start_x}, {abs_start_y}) to relative ({request.end_x:.3f}, {request.end_y:.3f}) -> absolute ({abs_end_x}, {abs_end_y}) with {request.button} button"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to drag: {str(e)}")

@app.post("/auto_start")
async def auto_start_game(request: AutoStartRequest):
    """Configure and trigger auto-start"""
    try:
        import json
        config = {
            "auto_start": True,
            "deck": request.deck,
            "stake": request.stake,
            "seed": request.seed if request.seed else "random"
        }
        
        with open("/tmp/balatro_auto_start.json", "w") as f:
            json.dump(config, f)
        
        return {"status": "configured", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/mod_status")
async def get_mod_status():
    """Get mod status"""
    try:
        import json
        with open("/tmp/balatro_mod_status.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": "no_status"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/mouse/position")
async def get_mouse_position():
    """Get current mouse position in both absolute and relative coordinates"""
    try:
        # Get absolute position
        abs_x, abs_y = pyautogui.position()
        
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        # Calculate relative position
        rel_x = abs_x / screen_width if screen_width > 0 else 0
        rel_y = abs_y / screen_height if screen_height > 0 else 0
        
        return {
            "absolute": {"x": abs_x, "y": abs_y},
            "relative": {"x": round(rel_x, 6), "y": round(rel_y, 6)},
            "screen_size": {"width": screen_width, "height": screen_height},
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mouse position: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Balatro Minimal API",
        "version": "1.0.0",
        "status": "running",
        "coordinate_system": "Relative coordinates (0-1) where 0 is top/left edge and 1 is bottom/right edge",
        "endpoints": {
            "start_game": "/start_balatro",
            "stop_game": "/stop_balatro",
            "auto_start": "/auto_start",
            "mod_status": "/mod_status",
            "gamepad_button": "/gamepad/buttons",
            "mouse_click": "/mouse/click (x, y as float 0-1)",
            "mouse_move": "/mouse/move (x, y as float 0-1)",
            "mouse_drag": "/mouse/drag (start_x, start_y, end_x, end_y as float 0-1)",
            "mouse_position": "/mouse/position",
            "screenshot": "/screenshot",
            "screenshot_with_cursor": "/screenshot_with_cursor",
            "health": "/health"
        }
    }

@app.get("/screenshot_with_cursor")
async def get_screenshot_with_cursor():
    """Screenshot con cursor visible"""
    try:
        # Verificar que X11 esté disponible
        if not wait_for_x11():
            raise HTTPException(status_code=503, detail="X11 server not available")
        
        # Capturar screenshot base
        result = subprocess.run(
            ['import', '-window', 'root', 'png:/tmp/screen_base.png'],
            capture_output=True,
            env={'DISPLAY': ':0'},
            timeout=10
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode() if result.stderr else "Unknown error"
            raise HTTPException(status_code=500, detail=f"Failed to capture screenshot: {error_msg}")
        
        # Obtener posición actual del mouse
        mouse_result = subprocess.run(
            ['xdotool', 'getmouselocation', '--shell'],
            capture_output=True, text=True,
            env={'DISPLAY': ':0'},
            timeout=5
        )
        
        mouse_x, mouse_y = 0, 0
        if mouse_result.returncode == 0:
            for line in mouse_result.stdout.strip().split('\n'):
                if line.startswith('X='):
                    mouse_x = int(line.split('=')[1])
                elif line.startswith('Y='):
                    mouse_y = int(line.split('=')[1])
        
        # Dibujar cursor en la imagen usando la nueva función
        img = Image.open('/tmp/screen_base.png')
        
        # Usar la función draw_point con color verde
        img = draw_point(img, [mouse_x, mouse_y], "green")
        
        # Convertir a bytes para respuesta
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return Response(content=img_buffer.getvalue(), media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot with cursor error: {e}")

@app.get("/screenshot")
async def get_screenshot():
    """Take a screenshot of the game"""
    try:
        result = subprocess.run(
            ['import', '-window', 'root', 'png:-'],
            capture_output=True,
            env={'DISPLAY': ':0'}
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")
        

        return Response(content=result.stdout, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot error: {e}")

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import os
import subprocess
import time
from typing import Optional
from pydantic import BaseModel
import uinput

ACTIONS_DONE = {}

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
                  DISPLAY=":1", 
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
        "endpoints": {
            "start_game": "/start_balatro",
            "stop_game": "/stop_balatro",
            "auto_start": "/auto_start",
            "mod_status": "/mod_status",
            "gamepad_button": "/gamepad/button",
            "screenshot": "/screenshot",
            "health": "/health"
        }
    }

@app.get("/screenshot")
async def get_screenshot():
    """Take a screenshot of the game"""
    try:
        result = subprocess.run(
            ['import', '-window', 'root', 'png:-'],
            capture_output=True,
            env={'DISPLAY': ':1'}
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")
        

        return Response(content=result.stdout, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot error: {e}")

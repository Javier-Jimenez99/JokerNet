from fastapi import FastAPI, HTTPException
import json, os
import subprocess
import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import contextlib

# Minimal Balatro Gamepad Controller
class BalatroGamepadController:
    def __init__(self):
        self.gamepad = None
        self.native_gamepad = None
        self.balatro_window_id = None
        self._init_controllers()
    
    def _init_controllers(self):
        """Initialize native uinput gamepad with vgamepad fallback"""
        # Try native uinput first
        try:
            self.native_gamepad = self._create_native_gamepad()
        except Exception:
            self.native_gamepad = None
        
        # vgamepad fallback
        try:
            import vgamepad as vg
            self.gamepad = vg.VX360Gamepad()
        except Exception:
            self.gamepad = None
    
    def _create_native_gamepad(self):
        """Create native gamepad using uinput"""
        import uinput
        
        events = [
            # Face buttons
            uinput.BTN_A, uinput.BTN_B, uinput.BTN_X, uinput.BTN_Y,
            # Shoulder buttons  
            uinput.BTN_TL, uinput.BTN_TR,
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
        """Press gamepad button with fallback priority: native -> vgamepad -> keyboard"""
        
        # Try native uinput first
        if self.native_gamepad:
            result = self._press_button_native(button_name, duration)
            if result["status"] == "success":
                return result
        
        # Fallback to vgamepad
        if self.gamepad:
            result = self._press_button_vgamepad(button_name, duration)
            if result["status"] == "success":
                return result
        
        # Last fallback: keyboard
        return self._press_button_keyboard(button_name, duration)
    
    def _press_button_native(self, button_name: str, duration: float):
        """Press button with native gamepad"""
        try:
            import uinput
            
            button_map = {
                'A': uinput.BTN_A,
                'B': uinput.BTN_B,
                'X': uinput.BTN_X,
                'Y': uinput.BTN_Y,
                'LB': uinput.BTN_TL,
                'RB': uinput.BTN_TR,
                'START': uinput.BTN_START,
                'BACK': uinput.BTN_SELECT,
                'SELECT': uinput.BTN_SELECT,
            }
            
            dpad_map = {
                'DPAD_UP': (uinput.ABS_HAT0Y, -1),
                'DPAD_DOWN': (uinput.ABS_HAT0Y, 1),
                'DPAD_LEFT': (uinput.ABS_HAT0X, -1),
                'DPAD_RIGHT': (uinput.ABS_HAT0X, 1),
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
    
    def _press_button_vgamepad(self, button_name: str, duration: float):
        """Press button with vgamepad fallback"""
        try:
            import vgamepad as vg
            
            button_map = {
                'A': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
                'B': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
                'X': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
                'Y': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
                'LB': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
                'RB': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
                'START': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
                'BACK': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
                'DPAD_UP': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                'DPAD_DOWN': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                'DPAD_LEFT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
                'DPAD_RIGHT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            }
            
            button = button_map.get(button_name.upper())
            if not button:
                return {"status": "error", "message": f"Button '{button_name}' not recognized"}
            
            self.focus_balatro_window()
            
            self.gamepad.press_button(button)
            self.gamepad.update()
            time.sleep(duration)
            self.gamepad.release_button(button)
            self.gamepad.update()
            
            return {
                "status": "success",
                "message": f"Button {button_name} pressed (vgamepad)",
                "method": "vgamepad"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"vgamepad error: {e}"}
    
    def _press_button_keyboard(self, button_name: str, duration: float):
        """Keyboard fallback for button presses"""
        try:
            import uinput
            
            key_map = {
                'A': uinput.KEY_SPACE,
                'B': uinput.KEY_ESC,
                'X': uinput.KEY_X,
                'Y': uinput.KEY_Y,
                'START': uinput.KEY_ENTER,
                'BACK': uinput.KEY_TAB,
                'DPAD_UP': uinput.KEY_UP,
                'DPAD_DOWN': uinput.KEY_DOWN,
                'DPAD_LEFT': uinput.KEY_LEFT,
                'DPAD_RIGHT': uinput.KEY_RIGHT,
                'LB': uinput.KEY_Q,
                'RB': uinput.KEY_E,
            }
            
            key = key_map.get(button_name.upper())
            if not key:
                return {"status": "error", "message": f"Button '{button_name}' has no keyboard mapping"}
            
            self.focus_balatro_window()
            
            events = [key]
            with uinput.Device(events, name="BalatroKeyboard") as kbd:
                kbd.emit_click(key)
                time.sleep(duration)
            
            return {
                "status": "success",
                "message": f"Button {button_name} sent as keyboard",
                "method": "keyboard_fallback"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Keyboard fallback error: {e}"}

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
class LogEvent(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: int

class GamepadButtonRequest(BaseModel):
    button: str
    duration: Optional[float] = 0.1

# Global state
logger_state = {
    "events_received": 0,
    "last_event": None,
    "last_event_time": None,
    "game_state": {},
    "balatro_running": False
}

balatro_process: Optional[subprocess.Popen] = None
gamepad_controller = BalatroGamepadController()

app = FastAPI(
    title="Balatro Minimal API",
    description="Minimal API for Balatro gamepad control",
    version="1.0.0"
)

@app.post("/logger/event")
async def receive_log_event(event: LogEvent):
    """Receive events from BalatroLogger mod"""
    try:
        global logger_state
        
        logger_state["events_received"] += 1
        logger_state["last_event"] = event.dict()
        logger_state["last_event_time"] = time.time()
        
        if event.type == "game_state":
            logger_state["game_state"] = event.data
            logger_state["balatro_running"] = True
            
        return {
            "status": "success", 
            "message": "Event logged",
            "event_count": logger_state["events_received"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing event: {e}")

@app.get("/logger/status")
async def get_logger_status():
    """Logger status and last activity"""
    return {
        "status": "active",
        "events_received": logger_state["events_received"],
        "last_event_time": logger_state["last_event_time"],
        "balatro_running": logger_state["balatro_running"]
    }

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
        
        logger_state["balatro_running"] = True
        
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
        
        logger_state["balatro_running"] = False
        balatro_process = None
        
        return {"status": "stopped"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping Balatro: {e}")

@app.post("/gamepad/button")
async def press_gamepad_button(request: GamepadButtonRequest):
    """Press gamepad button"""
    global gamepad_controller
    result = gamepad_controller.press_button(request.button, request.duration)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.get("/status")
async def get_status():
    """System status"""
    return {
        "api_status": "running",
        "balatro_running": logger_state["balatro_running"],
        "gamepad_available": gamepad_controller.gamepad is not None or gamepad_controller.native_gamepad is not None,
        "events_received": logger_state["events_received"]
    }

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
            "logger_status": "/logger/status",
            "start_game": "/start_balatro",
            "stop_game": "/stop_balatro",
            "gamepad_button": "/gamepad/button",
            "system_status": "/status",
            "health": "/health"
        }
    }

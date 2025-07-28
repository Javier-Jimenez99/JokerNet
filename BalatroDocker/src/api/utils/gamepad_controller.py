"""
Gamepad controller for handling input to Balatro game.
"""
import subprocess
import time
from typing import Optional, Dict, Any

try:
    import uinput
    UINPUT_AVAILABLE = True
except ImportError:
    print("Warning: uinput module not available. Gamepad functionality will be limited.")
    uinput = None
    UINPUT_AVAILABLE = False


class BalatroGamepadController:
    """Controller for handling gamepad inputs to Balatro."""
    
    def __init__(self):
        self.native_gamepad = None
        self.balatro_window_id = None
        self._init_controllers()
    
    def _init_controllers(self):
        """Initialize native uinput gamepad."""
        try:
            if UINPUT_AVAILABLE:
                self.native_gamepad = self._create_native_gamepad()
            else:
                self.native_gamepad = None
        except Exception as e:
            print(f"Failed to initialize native gamepad: {e}")
            self.native_gamepad = None
    
    def _create_native_gamepad(self):
        """Create native gamepad using uinput."""
        if not UINPUT_AVAILABLE:
            return None
            
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
        
        # Reset to neutral state
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
    
    def find_balatro_window(self) -> Optional[str]:
        """Find Balatro window using wmctrl."""
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
    
    def focus_balatro_window(self) -> bool:
        """Focus Balatro window."""
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
    
    def press_button(self, button_name: str, duration: float = 0.1) -> Dict[str, Any]:
        """Press gamepad button using native uinput."""
        
        if not self.native_gamepad:
            return {"status": "error", "message": "Native gamepad not available (uinput may not be installed)"}
        
        return self._press_button_native(button_name, duration)
    
    def _press_button_native(self, button_name: str, duration: float) -> Dict[str, Any]:
        """Press button with native gamepad."""
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

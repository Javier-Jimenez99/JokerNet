"""
X11 display and system utilities.
"""
import os
import subprocess
import time
from typing import Tuple


def wait_for_x11(max_attempts: int = 30) -> bool:
    """
    Wait for X11 server to be available.
    
    Args:
        max_attempts: Maximum number of attempts to check X11 availability
        
    Returns:
        bool: True if X11 is available, False otherwise
    """
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


def ensure_xauth() -> bool:
    """
    Ensure X11 authorization is properly set up.
    
    Returns:
        bool: True if X11 auth is set up successfully, False otherwise
    """
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


def relative_to_absolute(rel_x: float, rel_y: float, screen_width: int, screen_height: int) -> Tuple[int, int]:
    """
    Convert relative coordinates (0-1) to absolute screen coordinates.
    
    Args:
        rel_x: Relative X coordinate (0.0 to 1.0)
        rel_y: Relative Y coordinate (0.0 to 1.0)
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        
    Returns:
        Tuple[int, int]: Absolute coordinates (x, y)
    """
    # Clamp values to 0-1 range
    rel_x = max(0.0, min(1.0, rel_x))
    rel_y = max(0.0, min(1.0, rel_y))
    
    # Convert to absolute coordinates
    abs_x = int(rel_x * screen_width)
    abs_y = int(rel_y * screen_height)
    
    return abs_x, abs_y

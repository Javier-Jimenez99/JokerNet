"""
Screenshot controller for capturing game state and providing visual feedback.
"""
import subprocess
import time
from PIL import Image
from fastapi import HTTPException
from fastapi.responses import Response

from api.utils.system import wait_for_x11
from api.utils.image_processing import draw_point, image_to_bytes


async def get_screenshot() -> Response:
    """Take a screenshot of the current screen."""
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


async def get_screenshot_with_cursor() -> Response:
    """Take screenshot with visible cursor position marked."""
    try:
        # Verify X11 is available
        if not wait_for_x11():
            raise HTTPException(status_code=503, detail="X11 server not available")
        
        # Capture base screenshot
        result = subprocess.run(
            ['import', '-window', 'root', 'png:/tmp/screen_base.png'],
            capture_output=True,
            env={'DISPLAY': ':0'},
            timeout=10
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode() if result.stderr else "Unknown error"
            raise HTTPException(status_code=500, detail=f"Failed to capture screenshot: {error_msg}")
        
        # Get current mouse position
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
        
        # Load image and draw cursor position
        img = Image.open('/tmp/screen_base.png')
        img = draw_point(img, [mouse_x, mouse_y], "green")
        
        # Convert to bytes for response
        img_bytes = image_to_bytes(img, 'PNG')
        
        return Response(content=img_bytes, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot with cursor error: {e}")

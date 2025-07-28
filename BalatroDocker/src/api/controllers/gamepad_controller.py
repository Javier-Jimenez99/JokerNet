"""
Gamepad input controller for handling button presses and game control.
"""
import time
from typing import Dict, Any
from fastapi import HTTPException

from api.models.requests import GamepadButtonsRequest
from api.utils.gamepad_controller import BalatroGamepadController

# Global state for actions tracking
ACTIONS_DONE = {}

# Initialize gamepad controller
gamepad_controller = BalatroGamepadController()


async def press_gamepad_button(request: GamepadButtonsRequest) -> Dict[str, Any]:
    """Press one or more gamepad buttons."""
    global gamepad_controller

    buttons = request.buttons.split()
    if not buttons:
        raise HTTPException(status_code=400, detail="No buttons specified")
    
    valid_buttons = [
        'A', 'B', 'X', 'Y', 'LB', 'RB', 'LT', 'RT',
        'START', 'BACK', 'SELECT', 'UP', 'DOWN', 'LEFT', 'RIGHT'
    ]
    
    result = None
    success = True

    for button in buttons:
        button = button.strip().upper()
        if button not in valid_buttons:
            raise HTTPException(status_code=400, detail=f"Invalid button: {button}")
        
        result = gamepad_controller.press_button(button, request.duration)
        
        time.sleep(1)  # Wait between button presses
    
        if result["status"] == "error":
            success = False
            break
            
    # Store action in global state for tracking
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

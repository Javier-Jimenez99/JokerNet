"""
Game management controller for starting/stopping Balatro and managing game state.
"""
import os
import subprocess
import json
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException

from api.utils.config import get_config
from api.models.requests import AutoStartRequest

# Global game state
balatro_running = False
balatro_process: Optional[subprocess.Popen] = None


async def start_balatro() -> Dict[str, Any]:
    """Start Balatro with mods using Lovely."""
    global balatro_process
    
    try:
        if balatro_process and balatro_process.poll() is None:
            return {
                "status": "already_running",
                "pid": balatro_process.pid
            }
        
        config = get_config()
        cmd = config['BALATRO_CMD'].split()
        
        env = dict(os.environ, 
                  DISPLAY=":0", 
                  LD_PRELOAD=config['LOVELY_PRELOAD'],
                  LOVELY_MOD_DIR=config['LOVELY_MODS_DIR'])
        
        if not os.path.exists(config['LOVELY_MODS_DIR']):
            os.makedirs(config['LOVELY_MODS_DIR'], exist_ok=True)
        
        balatro_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=config['BALATRO_LOVE_DIR']
        )
        
        global balatro_running
        balatro_running = True
        
        return {
            "status": "started",
            "pid": balatro_process.pid
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting Balatro: {e}")


async def stop_balatro() -> Dict[str, Any]:
    """Stop Balatro game."""
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


async def auto_start_game(request: AutoStartRequest) -> Dict[str, Any]:
    """Configure and trigger auto-start with specific deck, stake, and seed."""
    try:
        config = {
            "auto_start": True,
            "deck": request.deck,
            "stake": request.stake,
            "seed": request.seed if request.seed else "random"
        }
        
        with open("/tmp/balatro_auto_start.json", "w") as f:
            json.dump(config, f)
        
        return {"status": "success", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


async def get_mod_status() -> Dict[str, Any]:
    """Get current mod status."""
    try:
        with open("/tmp/balatro_mod_status.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": "no_status"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

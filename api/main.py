from fastapi import FastAPI, HTTPException
import json, os
import subprocess
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel
import contextlib
from contextlib import asynccontextmanager

# Cargar configuración desde archivo
def load_config():
    config = {}
    config_file = "/etc/app/paths.env"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Expandir variables de entorno y limpiar comillas
                    value = os.path.expandvars(value.strip('"'))
                    config[key] = value
    
    # Derivar rutas automáticamente
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

# Configuración global
CONFIG = load_config()
LOVELY_MODS_DIR = CONFIG.get('LOVELY_MODS_DIR', '/root/.local/share/Balatro/Mods')
BALATRO_CMD = CONFIG.get('BALATRO_CMD', 'love .')
BALATRO_LOVE_DIR = CONFIG.get('BALATRO_LOVE_DIR', '/opt/balatro-love')
LOVELY_PRELOAD = CONFIG.get('LOVELY_PRELOAD', '/opt/lovely/liblovely.so')

# Modelos para la API
class LogEvent(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: int

# Estado del logger
logger_state = {
    "events_received": 0,
    "last_event": None,
    "last_event_time": None,
    "game_state": {},
    "balatro_running": False
}

# Variables globales
balatro_process: Optional[subprocess.Popen] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    print("🚀 Iniciando API de Balatro con BalatroLogger...")
    print(f"📁 Mods en: {LOVELY_MODS_DIR}")
    print(f"🎮 Directorio Love2D: {BALATRO_LOVE_DIR}")
    print(f"🎮 Comando Balatro: {BALATRO_CMD}")
    print(f"🎮 LD_PRELOAD: {LOVELY_PRELOAD}")
    
    # Verificar configuración de mods al inicio
    print(f"🔧 Verificando configuración de mods...")
    print(f"🔧 LOVELY_MOD_DIR (env): {os.environ.get('LOVELY_MOD_DIR', 'No configurada')}")
    print(f"🔧 LOVELY_MODS_DIR (config): {LOVELY_MODS_DIR}")
    print(f"🔧 Lovely existe: {os.path.exists(LOVELY_PRELOAD)}")
    
    if os.path.exists(LOVELY_MODS_DIR):
        mods = [d for d in os.listdir(LOVELY_MODS_DIR) if os.path.isdir(os.path.join(LOVELY_MODS_DIR, d))]
        print(f"🎮 Mods disponibles al inicio: {mods}")
    else:
        print(f"⚠️  Directorio de mods no existe: {LOVELY_MODS_DIR}")
    
    yield
    print("🛑 Cerrando API de Balatro...")
    
    # Limpiar procesos al cerrar
    global balatro_process
    if balatro_process:
        print("🔄 Terminando proceso de Balatro...")
        balatro_process.terminate()
        try:
            balatro_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            balatro_process.kill()

app = FastAPI(
    title="Balatro Logger API",
    description="API para monitorear Balatro usando BalatroLogger mod",
    version="2.0.0",
    lifespan=lifespan
)

@app.post("/logger/event")
async def receive_log_event(event: LogEvent):
    """Recibe eventos del mod BalatroLogger"""
    try:
        global logger_state
        
        logger_state["events_received"] += 1
        logger_state["last_event"] = event.dict()
        logger_state["last_event_time"] = time.time()
        
        # Actualizar estado del juego si es un evento de estado
        if event.type == "game_state":
            logger_state["game_state"] = event.data
            logger_state["balatro_running"] = True
            
        print(f"📝 Evento recibido: {event.type} - {event.data}")
        
        return {
            "status": "success", 
            "message": "Event logged",
            "event_count": logger_state["events_received"]
        }
        
    except Exception as e:
        print(f"❌ Error procesando evento: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando evento: {e}")

@app.get("/logger/status")
async def get_logger_status():
    """Estado del logger y última actividad"""
    return {
        "status": "active",
        "logger": "BalatroLogger",
        "events_received": logger_state["events_received"],
        "last_event_time": logger_state["last_event_time"],
        "last_event": logger_state["last_event"],
        "game_state": logger_state["game_state"],
        "balatro_running": logger_state["balatro_running"]
    }

@app.get("/logger/events")
async def get_recent_events():
    """Obtener información de eventos recientes"""
    return {
        "total_events": logger_state["events_received"],
        "last_event": logger_state["last_event"],
        "game_state": logger_state["game_state"]
    }

@app.post("/start_balatro")
async def start_balatro():
    """Inicia Balatro con mods usando Lovely"""
    global balatro_process
    
    try:
        # Verificar si ya está ejecutándose
        if balatro_process and balatro_process.poll() is None:
            return {
                "status": "already_running",
                "pid": balatro_process.pid,
                "message": "Balatro ya está ejecutándose"
            }
        
        # Usar el comando configurado
        cmd = BALATRO_CMD.split()
        
        print(f"🎮 Iniciando Balatro con: {' '.join(cmd)}")
        print(f"🎮 LD_PRELOAD: {LOVELY_PRELOAD}")
        
        # Preparar el entorno con LD_PRELOAD y configuración de mods
        env = dict(os.environ, 
                  DISPLAY=":1", 
                  LD_PRELOAD=LOVELY_PRELOAD,
                  LOVELY_MOD_DIR=LOVELY_MODS_DIR)  # Lovely espera LOVELY_MOD_DIR sin S
        
        print(f"📁 Directorio de mods configurado: {LOVELY_MODS_DIR}")
        print(f"🔧 Variable LOVELY_MOD_DIR: {LOVELY_MODS_DIR}")
        
        # Verificar que el directorio de mods existe
        if not os.path.exists(LOVELY_MODS_DIR):
            print(f"⚠️  Creando directorio de mods: {LOVELY_MODS_DIR}")
            os.makedirs(LOVELY_MODS_DIR, exist_ok=True)
        
        # Listar mods disponibles
        try:
            if os.path.exists(LOVELY_MODS_DIR):
                mods = [d for d in os.listdir(LOVELY_MODS_DIR) if os.path.isdir(os.path.join(LOVELY_MODS_DIR, d))]
                print(f"🎮 Mods encontrados: {mods}")
            else:
                print("⚠️  Directorio de mods no existe aún")
        except Exception as e:
            print(f"⚠️  Error listando mods: {e}")
        
        # Iniciar el proceso
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
            "pid": balatro_process.pid,
            "message": "Balatro iniciado con BalatroLogger",
            "command": " ".join(cmd)
        }
        
    except Exception as e:
        print(f"❌ Error iniciando Balatro: {e}")
        raise HTTPException(status_code=500, detail=f"Error iniciando Balatro: {e}")

@app.post("/stop_balatro")
async def stop_balatro():
    """Detiene Balatro"""
    global balatro_process
    
    try:
        if not balatro_process:
            return {"status": "not_running", "message": "Balatro no está ejecutándose"}
        
        if balatro_process.poll() is not None:
            return {"status": "already_stopped", "message": "Balatro ya se detuvo"}
        
        balatro_process.terminate()
        try:
            balatro_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            balatro_process.kill()
            balatro_process.wait()
        
        logger_state["balatro_running"] = False
        balatro_process = None
        
        return {"status": "stopped", "message": "Balatro detenido correctamente"}
        
    except Exception as e:
        print(f"❌ Error deteniendo Balatro: {e}")
        raise HTTPException(status_code=500, detail=f"Error deteniendo Balatro: {e}")

@app.get("/status")
async def get_status():
    """Estado general del sistema"""
    return {
        "api_status": "running",
        "balatro_running": logger_state["balatro_running"],
        "mods_directory": LOVELY_MODS_DIR,
        "balatro_love_dir": BALATRO_LOVE_DIR,
        "balatro_command": BALATRO_CMD,
        "lovely_preload": LOVELY_PRELOAD,
        "events_received": logger_state["events_received"],
    }

@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/")
async def root():
    """Información básica de la API"""
    return {
        "name": "Balatro Logger API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "logger_status": "/logger/status",
            "logger_events": "/logger/events", 
            "start_game": "/start_balatro",
            "stop_game": "/stop_balatro",
            "system_status": "/status",
            "mods_status": "/mods/status"
        }
    }

@app.get("/mods/status")
async def get_mods_status():
    """Estado de los mods instalados y configuración de Lovely"""
    try:
        mods_info = {
            "mods_directory": LOVELY_MODS_DIR,
            "directory_exists": os.path.exists(LOVELY_MODS_DIR),
            "lovely_preload": LOVELY_PRELOAD,
            "lovely_exists": os.path.exists(LOVELY_PRELOAD),
            "installed_mods": [],
            "environment_vars": {
                "LOVELY_MOD_DIR": os.environ.get("LOVELY_MOD_DIR"),
                "LOVELY_MODS_DIR": os.environ.get("LOVELY_MODS_DIR"),
                "LD_PRELOAD": os.environ.get("LD_PRELOAD")
            }
        }
        
        # Listar mods instalados
        if os.path.exists(LOVELY_MODS_DIR):
            for item in os.listdir(LOVELY_MODS_DIR):
                item_path = os.path.join(LOVELY_MODS_DIR, item)
                if os.path.isdir(item_path):
                    # Buscar archivos de configuración del mod
                    config_files = []
                    for root, dirs, files in os.walk(item_path):
                        for file in files:
                            if file.endswith(('.lua', '.json', '.toml')):
                                config_files.append(os.path.join(root, file))
                    
                    mods_info["installed_mods"].append({
                        "name": item,
                        "path": item_path,
                        "config_files": config_files[:5]  # Limitar a 5 archivos
                    })
        
        return mods_info
        
    except Exception as e:
        print(f"❌ Error obteniendo estado de mods: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado de mods: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

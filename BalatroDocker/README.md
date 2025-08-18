# 🃏 Balatro Docker con noVNC + Streamlit

Esta implementación ejecuta Balatro en un contenedor Docker con acceso remoto a través de **noVNC** (cliente web) integrado en una aplicación **Streamlit**.

## 🚀 Características

- ✅ **Balatro** ejecutándose automáticamente
- ✅ **noVNC** como cliente web para acceso remoto
- ✅ **API REST** para automatización
- ✅ **MCP Server** para integración con IA
- ✅ **Logs** centralizados con Supervisor
- ✅ **Resolución 1920x1080** optimizada para gaming
- ✅ **Streamlit externo** para interfaz opcional
- ✅ **Caché persistente** de modelos Hugging Face

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Streamlit       │────│     noVNC        │────│      VNC        │
│ (Externo 8501)  │    │   (Puerto 6080)  │    │  (Puerto 5900)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                ┌───────────────┐
                                                │   Balatro     │
                                                │ (Xvfb + Love2D)│
                                                └───────────────┘
```

## 🔧 Instalación y Uso

### 1. Configurar el host (REQUERIDO)

Antes de ejecutar el contenedor, ejecuta en el host:

```bash
# Cargar módulo uinput
sudo modprobe uinput

# Dar permisos al dispositivo
sudo chmod 666 /dev/uinput
```

#### WSL2 + GPU (Opcional)

Para usar GPU en WSL2, sigue la [guía oficial](https://docs.nvidia.com/cuda/wsl-user-guide/index.html):

```bash
# 1. Instalar NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit nvidia-modprobe

# 2. Configurar Docker daemon
sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
EOF

sudo systemctl restart docker

# 3. Crear dispositivos NVIDIA (ejecutar después de cada reinicio)
sudo nvidia-modprobe -u -c=0 || {
    sudo mknod /dev/nvidia0 c 195 0
    sudo mknod /dev/nvidiactl c 195 255
    sudo mknod /dev/nvidia-modeset c 195 254
    sudo mknod /dev/nvidia-uvm c 243 0
    sudo chmod 666 /dev/nvidia*
}
```

**Error común**: "GPU access blocked by the operating system"
- **Solución**: Usar `privileged: true` en docker-compose (ya incluido)

### 2. Construir y ejecutar el contenedor:

```bash
cd BalatroDocker
docker-compose up -d
```

### 3. Construir y ejecutar el contenedor:

```bash
cd BalatroDocker
docker-compose up -d
```

**Nota**: La primera vez que se use el locator visual, los modelos de Hugging Face se descargarán automáticamente (puede tomar 5-10 minutos). Los modelos se almacenan en `./data/huggingface/` y persisten entre reinicios.

### 4. Acceder a los servicios:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **🖥️ noVNC directo** | http://localhost:6080 | **Cliente noVNC principal** |
| **🔌 API REST** | http://localhost:8000/docs | Documentación automática de la API |
| **🧠 MCP Server** | http://localhost:8001 | Servidor MCP para IA |
| **📺 VNC tradicional** | `localhost:5900` | Para clientes VNC nativos |

### 4. Ejecutar Streamlit (opcional):

Para usar la interfaz Streamlit, ejecuta desde fuera del Docker:

```bash
# Instalar dependencias (una sola vez)
pip install streamlit

# Ejecutar la interfaz
cd src
streamlit run streamlit_app.py
```

Entonces tendrás también:
- **🌐 Streamlit** | http://localhost:8501 | Interfaz moderna con noVNC integrado

## 🎮 Uso de la Interfaz

### Opción 1: noVNC directo (incluido en Docker):
1. Abre **http://localhost:6080**
2. Clic en "Connect" 
3. Usa mouse y teclado normalmente
4. Pantalla completa disponible en la barra de herramientas

### Opción 2: Streamlit + noVNC (externo):
1. Ejecuta: `cd src && streamlit run streamlit_app.py`
2. Abre **http://localhost:8501**
3. La conexión a Balatro es **automática**
4. Interfaz moderna con instrucciones integradas

### Control por API:
```bash
# Presionar botón A
curl -X POST "http://localhost:8000/gamepad/button" \
     -H "Content-Type: application/json" \
     -d '{"button": "A", "duration": 0.1}'

# Auto-iniciar juego
curl -X POST "http://localhost:8000/auto_start" \
     -H "Content-Type: application/json" \
     -d '{"auto_start": true, "deck": "b_blue", "stake": 3}'

# Capturar pantalla
curl "http://localhost:8000/screenshot" > screenshot.png
```

## 📁 Estructura del Proyecto

```
BalatroDocker/
├── 🐳 Dockerfile                 # Imagen con Balatro + noVNC
├── 🎛️ docker-compose.yml         # Orquestación de servicios
├── 📦 requirements.txt           # Dependencias Python (sin Streamlit)
├── config/
│   ├── supervisord.conf       # ⚙️ Configuración de procesos
│   └── paths.env             # 🔧 Variables de entorno
├── scripts/
│   ├── setup_novnc.sh        # 🎨 Configuración personalizada de noVNC
│   ├── startup.sh            # 🚀 Script de inicio
│   └── ...
└── src/
    ├── api.py               # 🔌 API REST
    └── mcp_server.py        # 🧠 Servidor MCP

# Fuera del Docker:
src/
└── streamlit_app.py         # 🌐 App Streamlit opcional (externa)
```

## 🔍 Servicios Supervisados

Todos los servicios se gestionan con **Supervisor**:

1. **🖥️ Xvfb** - Servidor X virtual (display :0)
2. **📺 x11vnc** - Servidor VNC (puerto 5900)
3. **🌐 noVNC** - Proxy WebSocket (puerto 6080)
4. **🔌 API** - Servidor FastAPI (puerto 8000)
5. **🧠 MCP** - Servidor MCP (puerto 8001)

## 🎯 Auto-Inicio de Partidas

Configura partidas automáticas con diferentes mazos y apuestas:

### Mazos Disponibles:
- `b_red` - Mazo Rojo (predeterminado)
- `b_blue` - Mazo Azul
- `b_magic` - Mazo Mágico
- `b_nebula` - Mazo Nebulosa
- `b_ghost` - Mazo Fantasma
- `b_plasma` - Mazo Plasma

### Apuestas (Stakes):
1. **Blanca** (más fácil) → 8. **Dorada** (más difícil)

### Ejemplo de uso:
```bash
# Iniciar con mazo mágico, apuesta 5
curl -X POST "http://localhost:8000/auto_start" \
     -H "Content-Type: application/json" \
     -d '{"auto_start": true, "deck": "b_magic", "stake": 5, "seed": "EPIC2024"}'
```

## 🛠️ Desarrollo

### Rebuilding:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Debug mode:
```bash
docker-compose exec balatro bash
supervisorctl status
```

### Logs:
```bash
# Ver todos los logs
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f balatro
```

## 📊 Monitoreo

### Estado de servicios:
```bash
docker exec -it $(docker-compose ps -q) supervisorctl status
```

### Verificar conexiones:
```bash
# VNC
nc -zv localhost 5900

# noVNC  
curl -I http://localhost:6080

# Streamlit
curl -I http://localhost:8501

# API
curl http://localhost:8000/health
```

## 🧠 Integración con IA (MCP)

El servidor MCP permite que agentes de IA controlen Balatro:

### Herramientas disponibles:
- **`press_buttons(sequence)`**: Presionar botones del gamepad
- **`get_screen()`**: Capturar pantalla (base64 PNG)

### Ejemplo con agente IA:
```python
import requests

# Conectar con el MCP server
mcp_url = "http://localhost:8001/mcp"

# Obtener herramientas disponibles
response = requests.post(mcp_url, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
})

# Presionar botones
response = requests.post(mcp_url, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "press_buttons",
        "arguments": {"sequence": "A A B START"}
    }
})
```

## 🔒 Seguridad

Para producción:

- [ ] **Autenticación VNC**: Agregar contraseña con `-passwd`
- [ ] **HTTPS**: Certificados SSL para noVNC
- [ ] **Firewall**: Limitar acceso a puertos específicos
- [ ] **VPN**: Acceso solo desde red privada

### Configuración segura:
```yaml
# docker-compose.yml
environment:
  - VNC_PASSWORD=tu_password_seguro
```

## 🐛 Troubleshooting

### ❌ noVNC no conecta
```bash
# Verificar que VNC está corriendo
docker exec container_name ps aux | grep x11vnc

# Verificar puerto
docker exec container_name netstat -tlnp | grep 5900
```

### ❌ Streamlit no carga el iframe
- Verificar que noVNC está en puerto 6080
- Revisar logs: `docker-compose logs streamlit`
- Comprobar que websockify está corriendo

### ❌ Balatro no responde a inputs
```bash
# Verificar dispositivo uinput en el host
ls -la /dev/uinput

# Verificar permisos
docker exec container_name ls -la /dev/uinput
```

### ❌ Servicios no inician
```bash
# Ver estado de supervisor
docker exec container_name supervisorctl status

# Reiniciar servicio específico
docker exec container_name supervisorctl restart novnc
```

## 📝 Notas Técnicas

- **Resolución**: 1920x1080 (configurable en `supervisord.conf`)
- **Sin audio**: Por limitaciones del contenedor
- **Input simulation**: Requiere privilegios para `/dev/uinput`
- **Persistencia**: 
  - Steam data en `./data/steam`
  - Modelos Hugging Face en `./data/huggingface`
- **Mods**: Auto-configurados con Lovely mod loader
- **Modelos IA**: PTA-1 para detección visual de elementos de UI

## 🆚 Comparación con otras soluciones

| Característica | Esta implementación | Alternativas |
|----------------|-------------------|--------------|
| **Cliente web** | ✅ noVNC + Streamlit | ❌ Solo VNC nativo |
| **Auto-conexión** | ✅ Automática | ❌ Manual |
| **API REST** | ✅ Completa | ❌ Limitada |
| **IA Integration** | ✅ MCP Server | ❌ No disponible |
| **UI moderna** | ✅ Streamlit + CSS | ❌ Básica |
| **Gaming optimizado** | ✅ Configurado | ❌ General |

---

🎯 **Resultado Final**: Balatro ejecutándose en un navegador web con control total, APIs para automatización e integración con IA.

🚀 **Para empezar rápido**: 
1. `docker-compose up -d` 
2. **http://localhost:6080** (noVNC directo)

🎨 **Para interfaz moderna**: 
1. `cd src && streamlit run streamlit_app.py`
2. **http://localhost:8501** (Streamlit + noVNC)

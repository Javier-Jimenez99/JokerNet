# 🎮 JokerNet - Soporte de Controladores

Este proyecto ahora incluye soporte completo para controladores/gamepads para jugar Balatro.

## 🚀 Funcionalidades

- **Mapeo automático de botones** de Xbox, PlayStation y controladores genéricos
- **API REST** para enviar inputs desde aplicaciones externas
- **Simulación de inputs** usando xdotool y xboxdrv
- **Calibración automática** de controladores
- **Secuencias de comandos** para automatización

## 📡 Endpoints de la API

### Enviar input de controlador
```bash
POST /controller/input
{
    "button": "a",
    "action": "press",
    "duration": 0.1
}
```

### Enviar secuencia de inputs
```bash
POST /controller/sequence
[
    {"button": "a", "action": "press"},
    {"button": "dpad_right", "action": "press"},
    {"button": "b", "action": "press"}
]
```

### Obtener mapeo de botones
```bash
GET /controller/mapping
```

### Actualizar mapeo de botones
```bash
PUT /controller/mapping
{
    "a": "Return",
    "b": "Escape",
    "x": "space"
}
```

### Listar dispositivos de controlador
```bash
GET /controller/devices
```

### Calibrar controlador
```bash
POST /controller/calibrate
```

### Probar controlador
```bash
GET /controller/test
```

## 🎮 Mapeo de Botones por Defecto

### Xbox Controller
- **A** → Enter (Confirmar)
- **B** → Escape (Cancelar/Salir)
- **X** → Space (Acción especial)
- **Y** → Tab (Cambiar vista)
- **Start** → Enter (Pausar/Menú)
- **Select** → Escape (Salir)
- **LB** → Q (Navegación izquierda)
- **RB** → E (Navegación derecha)
- **LT** → 1 (Slot 1)
- **RT** → 2 (Slot 2)
- **D-Pad** → Flechas direccionales

### PlayStation Controller
- **Cross (✕)** → Enter
- **Circle (○)** → Escape
- **Square (□)** → Space
- **Triangle (△)** → Tab
- **L1** → Q
- **R1** → E
- **L2** → 1
- **R2** → 2

## 💻 Ejemplos de Uso

### Usando curl para enviar inputs:

```bash
# Presionar botón A
curl -X POST "http://localhost:8000/controller/input" \
     -H "Content-Type: application/json" \
     -d '{"button": "a", "action": "press"}'

# Navegación básica en el menú
curl -X POST "http://localhost:8000/controller/sequence" \
     -H "Content-Type: application/json" \
     -d '[
         {"button": "dpad_down", "action": "press"},
         {"button": "dpad_down", "action": "press"},
         {"button": "a", "action": "press"}
     ]'

# Mantener presionado un botón
curl -X POST "http://localhost:8000/controller/input" \
     -H "Content-Type: application/json" \
     -d '{"button": "x", "action": "hold", "duration": 2.0}'
```

### Usando Python:

```python
import requests
import time

API_BASE = "http://localhost:8000"

def send_button(button, action="press", duration=0.1):
    response = requests.post(f"{API_BASE}/controller/input", json={
        "button": button,
        "action": action,
        "duration": duration
    })
    return response.json()

def send_sequence(buttons):
    inputs = [{"button": btn, "action": "press"} for btn in buttons]
    response = requests.post(f"{API_BASE}/controller/sequence", json=inputs)
    return response.json()

# Ejemplos de uso
send_button("a")  # Presionar A
send_button("x", "hold", 1.5)  # Mantener X por 1.5 segundos
send_sequence(["dpad_right", "dpad_right", "a"])  # Navegar y confirmar
```

## 🔧 Configuración Avanzada

### Personalizar mapeo de botones:

```bash
curl -X PUT "http://localhost:8000/controller/mapping" \
     -H "Content-Type: application/json" \
     -d '{
         "a": "Return",
         "b": "Escape",
         "x": "space",
         "y": "Tab",
         "start": "p",
         "select": "m"
     }'
```

### Verificar dispositivos conectados:

```bash
curl -X GET "http://localhost:8000/controller/devices"
```

## 🎯 Casos de Uso

### Automatización de Gameplay
- **Navegación automática** por menús
- **Auto-play** de manos simples
- **Farming** automático de runs
- **Testing** de estrategias

### Accesibilidad
- **Inputs programados** para jugadores con limitaciones físicas
- **Macros personalizados** para acciones complejas
- **Control remoto** del juego

### Desarrollo y Testing
- **Pruebas automatizadas** de la UI del juego
- **Recolección de datos** de gameplay
- **Simulación de diferentes estilos** de juego

## 🐛 Troubleshooting

### Controlador no detectado:
```bash
# Verificar dispositivos
ls /dev/input/js*

# Verificar permisos
ls -la /dev/input/
```

### Inputs no funcionan:
```bash
# Verificar que el juego esté ejecutándose
curl -X GET "http://localhost:8000/balatro_status"

# Probar input básico
curl -X GET "http://localhost:8000/controller/test"
```

### Error de mapeo:
```bash
# Obtener mapeo actual
curl -X GET "http://localhost:8000/controller/mapping"

# Resetear a mapeo por defecto
curl -X PUT "http://localhost:8000/controller/mapping" \
     -H "Content-Type: application/json" \
     -d '{"a": "Return", "b": "Escape"}'
```

## 📝 Notas Técnicas

- Los inputs se envían usando **xdotool** a la ventana de Love2D
- **xboxdrv** maneja la traducción de controladores físicos a eventos de teclado
- La API permite **control tanto directo como por secuencias**
- Compatible con **controladores USB y Bluetooth**
- Funciona dentro del **entorno containerizado** con X11 forwarding

## 🔄 Integración con IA

Este sistema de controladores está diseñado para integrarse fácilmente con:
- **Modelos de RL** (Reinforcement Learning)
- **Bots de gameplay** automático
- **Sistemas de visión por computadora**
- **APIs de streaming** para control remoto

¡Listo para automatizar tu gameplay de Balatro! 🃏🤖

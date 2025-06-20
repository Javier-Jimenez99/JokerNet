# 🎮 Controlador Virtual - JokerNet

JokerNet incluye un **controlador virtual** que permite enviar acciones de gamepad al juego a través de la API REST, simulando un controlador físico.

## 🚀 Características

- ✅ **Controlador virtual completo** con todos los botones estándar
- ✅ **Mapeo personalizable** de botones a teclas del juego
- ✅ **Secuencias de acciones** para automatización
- ✅ **Estado del controlador** en tiempo real
- ✅ **Compatibilidad total** con Balatro

## 📡 API Endpoints

### Enviar Acción Individual
```bash
POST /controller/action
Content-Type: application/json

{
    "button": "a",
    "action": "press",
    "duration": 0.1
}
```

**Acciones disponibles:**
- `press` - Presionar y soltar inmediatamente
- `hold` - Mantener presionado por la duración especificada
- `release` - Soltar botón (para uso avanzado)

### Enviar Secuencia de Acciones
```bash
POST /controller/sequence
Content-Type: application/json

{
    "actions": [
        {"button": "a", "action": "press"},
        {"button": "dpad_right", "action": "press"},
        {"button": "b", "action": "press"}
    ],
    "delay_between_actions": 0.3
}
```

### Estado del Controlador
```bash
GET /controller/status
```

Retorna información completa del controlador virtual y físicos.

### Actualizar Mapeo de Botones
```bash
PUT /controller/mapping
Content-Type: application/json

{
    "a": "Return",
    "b": "Escape",
    "start": "p"
}
```

### Resetear Controlador
```bash
POST /controller/reset
```

### Prueba Rápida
```bash
GET /controller/test
```

## 🎮 Botones Disponibles

### Botones Principales
- `a` - Botón A (Confirmar)
- `b` - Botón B (Cancelar)
- `x` - Botón X (Acción especial)
- `y` - Botón Y (Menú/Vista)

### D-Pad
- `dpad_up` - D-pad Arriba
- `dpad_down` - D-pad Abajo
- `dpad_left` - D-pad Izquierda
- `dpad_right` - D-pad Derecha

### Shoulders y Triggers
- `lb` - Left Bumper (L1)
- `rb` - Right Bumper (R1)
- `lt` - Left Trigger (L2)
- `rt` - Right Trigger (R2)

### Botones del Sistema
- `start` - Botón Start (Menú/Pausa)
- `select` - Botón Select (Atrás)

### Sticks Analógicos
- `left_stick_up/down/left/right` - Stick izquierdo
- `right_stick_up/down/left/right` - Stick derecho

## 🗺️ Mapeo por Defecto

| Botón | Tecla | Función en Balatro |
|-------|-------|-------------------|
| `a` | Return | Confirmar/Seleccionar |
| `b` | Escape | Cancelar/Atrás |
| `x` | Space | Acción especial |
| `y` | Tab | Cambiar vista |
| `start` | Return | Menú/Pausa |
| `select` | Escape | Salir |
| `dpad_*` | Flechas | Navegación |
| `lb/rb` | Q/E | Navegación lateral |
| `lt/rt` | 1/2 | Slots/Acciones rápidas |

## 💻 Ejemplos de Uso

### Usando curl

```bash
# Presionar botón A
curl -X POST "http://localhost:8000/controller/action" \
     -H "Content-Type: application/json" \
     -d '{"button": "a", "action": "press"}'

# Mantener X presionado por 2 segundos
curl -X POST "http://localhost:8000/controller/action" \
     -H "Content-Type: application/json" \
     -d '{"button": "x", "action": "hold", "duration": 2.0}'

# Secuencia de navegación
curl -X POST "http://localhost:8000/controller/sequence" \
     -H "Content-Type: application/json" \
     -d '{
         "actions": [
             {"button": "dpad_down", "action": "press"},
             {"button": "dpad_down", "action": "press"},
             {"button": "a", "action": "press"}
         ],
         "delay_between_actions": 0.5
     }'

# Ver estado del controlador
curl -X GET "http://localhost:8000/controller/status"
```

### Usando Python

```python
import requests
import time

API_BASE = "http://localhost:8000"

class VirtualController:
    def __init__(self):
        self.base_url = API_BASE
    
    def press(self, button):
        """Presiona un botón"""
        response = requests.post(f"{self.base_url}/controller/action", json={
            "button": button,
            "action": "press"
        })
        return response.json()
    
    def hold(self, button, duration=1.0):
        """Mantiene un botón presionado"""
        response = requests.post(f"{self.base_url}/controller/action", json={
            "button": button,
            "action": "hold",
            "duration": duration
        })
        return response.json()
    
    def sequence(self, buttons, delay=0.3):
        """Ejecuta una secuencia de botones"""
        actions = [{"button": btn, "action": "press"} for btn in buttons]
        response = requests.post(f"{self.base_url}/controller/sequence", json={
            "actions": actions,
            "delay_between_actions": delay
        })
        return response.json()
    
    def status(self):
        """Obtiene el estado del controlador"""
        response = requests.get(f"{self.base_url}/controller/status")
        return response.json()

# Ejemplo de uso
controller = VirtualController()

# Confirmar algo
controller.press("a")

# Navegar en menú
controller.sequence(["dpad_down", "dpad_down", "a"])

# Mantener botón presionado
controller.hold("x", 2.0)

# Ver estado
print(controller.status())
```

### Usando JavaScript

```javascript
class VirtualController {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async press(button) {
        const response = await fetch(`${this.baseUrl}/controller/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                button: button,
                action: 'press'
            })
        });
        return response.json();
    }
    
    async sequence(buttons, delay = 0.3) {
        const actions = buttons.map(btn => ({
            button: btn,
            action: 'press'
        }));
        
        const response = await fetch(`${this.baseUrl}/controller/sequence`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actions: actions,
                delay_between_actions: delay
            })
        });
        return response.json();
    }
    
    async status() {
        const response = await fetch(`${this.baseUrl}/controller/status`);
        return response.json();
    }
}

// Uso
const controller = new VirtualController();

// Presionar A
await controller.press('a');

// Secuencia de navegación
await controller.sequence(['dpad_right', 'dpad_right', 'a']);
```

## 🎯 Casos de Uso

### Bot de Gameplay Automático
```python
def auto_play_hand():
    """Juega una mano automáticamente"""
    controller = VirtualController()
    
    # Seleccionar cartas (ejemplo básico)
    for i in range(5):
        controller.press("dpad_right")
        time.sleep(0.2)
        controller.press("a")
        time.sleep(0.2)
    
    # Jugar la mano
    controller.press("space")
    time.sleep(3)

def navigate_menu():
    """Navega por el menú principal"""
    controller = VirtualController()
    
    # Ir a nueva partida
    controller.sequence(["dpad_down", "dpad_down", "a"])
    time.sleep(2)
    
    # Confirmar configuración
    controller.press("a")
```

### Testing Automatizado
```python
def test_game_navigation():
    """Prueba la navegación del juego"""
    controller = VirtualController()
    
    # Test de todos los botones principales
    test_buttons = ["a", "b", "x", "y", "start", "select"]
    
    for button in test_buttons:
        print(f"Testing {button}...")
        result = controller.press(button)
        assert result["status"] == "success"
        time.sleep(0.5)
    
    print("All buttons working correctly!")
```

### Macros Personalizados
```python
def quick_restart():
    """Macro para reiniciar rápido"""
    controller = VirtualController()
    
    # Pausar, ir a menú principal, nueva partida
    controller.sequence([
        "start",      # Pausar
        "select",     # Salir
        "a",          # Confirmar
        "a"           # Nueva partida
    ], delay=1.0)

def shop_buy_all():
    """Comprar todo en la tienda"""
    controller = VirtualController()
    
    for _ in range(5):  # Máximo 5 items
        controller.press("a")  # Comprar
        controller.press("dpad_right")  # Siguiente item
        time.sleep(0.5)
```

## 🔧 Configuración Avanzada

### Personalizar Mapeo de Botones
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

### Verificar Estado en Tiempo Real
```python
def monitor_controller():
    """Monitorea el estado del controlador"""
    controller = VirtualController()
    
    while True:
        status = controller.status()
        virtual = status["virtual_controller"]
        
        print(f"Actions: {virtual['total_actions']}")
        print(f"Pressed: {virtual['buttons_pressed']}")
        print(f"Last: {virtual['last_action']}")
        
        time.sleep(1)
```

## 🐛 Troubleshooting

### Botón no responde
```bash
# Verificar que el juego esté ejecutándose
curl http://localhost:8000/balatro_status

# Verificar mapeo de botones
curl http://localhost:8000/controller/status
```

### Error de conexión
```bash
# Verificar que la API esté corriendo
curl http://localhost:8000/health

# Probar controlador virtual
curl http://localhost:8000/controller/test
```

### Resetear si hay problemas
```bash
# Resetear estado del controlador
curl -X POST http://localhost:8000/controller/reset
```

¡El controlador virtual está listo para automatizar tu gameplay de Balatro! 🎮🤖

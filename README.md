# JokerNet - Balatro con IA y Gamepad Virtual

Este proyecto permite ejecutar Balatro en un contenedor Docker con acceso remoto via VNC, una API para automatización y **gamepad virtual completo** que Balatro detecta como un controlador real.

## 🎮 Características Principales

- 🎯 **Gamepad virtual real** - Simula un controlador físico usando uinput
- 🖥️ **Acceso remoto via VNC** para visualización del juego
- 🔧 **API REST** para automatización y control
- 🎨 **Soporte completo de mods** via Lovely Injector
- 🤖 **Integración con IA** para gameplay automático
- 🐳 **Containerizado** para fácil despliegue

## 🚀 Inicio Rápido

### 1. Configurar credenciales de Steam

Crear un archivo `.env` con tus credenciales de Steam:

```bash
STEAM_USER=tu_usuario_steam
STEAM_PASS=tu_contraseña_steam
STEAM_GUARD=tu_codigo_steam_guard_opcional
```

### 2. Construir y ejecutar

```bash
docker-compose up --build
```

### 3. Conectar via VNC

Una vez que el contenedor esté ejecutándose:

- **Puerto VNC**: 5900
- **Resolución**: 1920x1080
- **Sin contraseña**

Usar cualquier cliente VNC (como RealVNC, TightVNC, o VNC Viewer):
```
localhost:5900
```

### 4. Conectar tu controlador

1. **Conecta tu controlador** via USB o Bluetooth antes de iniciar el contenedor
2. **Inicia Balatro** usando la API: `POST http://localhost:8000/start_balatro`
3. **¡Juega!** - Tu controlador será detectado automáticamente

## 🎮 Soporte de Controladores

### Controladores Compatibles
- ✅ **Xbox 360/One/Series** (USB y Wireless)
- ✅ **PlayStation 3/4/5** (DualShock/DualSense)
- ✅ **Nintendo Switch Pro Controller**
- ✅ **Controladores genéricos** compatibles con SDL2
- ✅ **Steam Controller**

### Verificar Controladores
```bash
# Verificar estado de controladores
curl http://localhost:8000/controller/status

# Probar funcionalidad
curl http://localhost:8000/controller/test
```

### 4. API Endpoints

El servidor API estará disponible en `http://localhost:8000`

#### Endpoints del Juego:

- `GET /health` - Estado del servidor
- `GET /vnc_info` - Información de conexión VNC
- `GET /balatro_status` - Estado del juego Balatro
- `GET /balatro_methods` - Información del método de ejecución
- `GET /mods_info` - Información sobre mods instalados
- `POST /start_balatro` - Iniciar Balatro con soporte de controladores y mods
- `POST /stop_balatro` - Detener Balatro
- `POST /reset` - Reset del juego (IA)
- `POST /step` - Paso de IA

#### Endpoints de Controladores:

- `GET /controller/status` - Estado y dispositivos de controladores detectados
- `GET /controller/test` - Probar funcionalidad de controladores

### 5. Usar la API

```bash
# Verificar estado
curl http://localhost:8000/health

# Información VNC
curl http://localhost:8000/vnc_info

# Ver información del método de ejecución
curl http://localhost:8000/balatro_methods

# Ver información de mods
curl http://localhost:8000/mods_info

# Iniciar Balatro con Lovely Injector (mods habilitados)
curl -X POST http://localhost:8000/start_balatro

# Ver estado de Balatro
curl http://localhost:8000/balatro_status

# Detener Balatro
curl -X POST http://localhost:8000/stop_balatro

# Verificar estado de controladores
curl http://localhost:8000/controller/status

# Probar funcionalidad de controladores
curl http://localhost:8000/controller/test
```

## 🎮 Flujo de Trabajo

1. **Iniciar el contenedor**: `docker-compose up --build`
2. **Esperar inicialización**: Los logs mostrarán cuando esté listo
3. **Conectar VNC**: Cliente VNC a `localhost:5900`
4. **Iniciar Balatro**: `curl -X POST http://localhost:8000/start_balatro`
5. **Jugar**: El juego aparecerá en la sesión VNC con soporte completo para mods

## 🧩 Sistema de Mods

Este proyecto incluye **Lovely Injector** integrado obligatoriamente para soporte completo de mods de Balatro.

### Funcionamiento de los Mods

- **Lovely Injector**: Se descarga automáticamente la versión `v0.8.0` para Linux nativo
- **Love2D Nativo**: Ejecutamos Balatro directamente con Love2D + LD_PRELOAD
- **Directorio de mods**: `/root/.local/share/Balatro/Mods`
- **Soporte completo**: Todos los mods compatibles con Lovely funcionarán automáticamente

### Usar Mods

1. **Configurar MOD_URLS**: Añadir URLs de mods en el archivo `.env`
2. **Construcción automática**: Los mods se descargan durante el build
3. **Ejecución**: Todos los comandos usan Lovely automáticamente

### Configuración de Mods

Añadir URLs de mods en tu archivo `.env`:

```bash
MOD_URLS=https://github.com/ejemplo/mod1/archive/main.zip,https://github.com/ejemplo/mod2/archive/main.zip
```

### Verificar Mods

```bash
# Ver información de mods instalados
curl http://localhost:8000/mods_info

# Ver información del sistema
curl http://localhost:8000/balatro_methods
```

## 📦 Gestión de Mods

### API de Mods

```bash
# Obtener información completa sobre mods
curl http://localhost:8000/mods_info
```

La respuesta incluye:
- Estado de Lovely Injector
- Directorio de mods
- Lista de mods instalados
- Conteo de mods

### Instalación Manual de Mods

Los mods se instalan en `/root/.local/share/Balatro/Mods/` dentro del contenedor y se cargan automáticamente cuando Balatro se ejecuta con Lovely Injector.

## 🐛 Resolución de Problemas

### Balatro no se inicia

1. Verificar que Steam haya descargado el juego:
   ```bash
   curl http://localhost:8000/balatro_status
   ```

2. Verificar logs del contenedor:
   ```bash
   docker-compose logs -f
   ```

3. Conectar via VNC y verificar errores de Love2D

### Los mods no funcionan

1. Verificar que lovely esté instalado correctamente:
   ```bash
   curl http://localhost:8000/mods_status
   ```

2. Verificar logs del contenedor para errores de lovely:
   ```bash
   docker-compose logs -f
   ```

3. Los mods deben estar en formato correcto con archivos `lovely.toml`

### VNC no se conecta

1. Verificar que el puerto 5900 esté disponible
2. Reiniciar el contenedor si es necesario
3. Verificar logs de X11/VNC en el contenedor

### Steam no descarga Balatro

1. Verificar credenciales en `.env`
2. Balatro debe estar en tu biblioteca de Steam
3. Algunos juegos pueden no estar disponibles en plataforma Linux

## 📁 Estructura del Proyecto

```
JokerNet/
├── api/                    # Servidor FastAPI
│   └── main.py            # Endpoints de la API
├── config/                # Configuración
│   └── supervisord.conf   # Config de supervisor
├── scripts/               # Scripts de utilidad
│   ├── get_mods.sh       # Descarga de mods
│   └── startup.sh        # Script de inicio
├── data/steam/           # Datos persistentes de Steam
├── docker-compose.yml   # Configuración Docker
├── Dockerfile           # Imagen Docker
└── requirements.txt     # Dependencias Python
```

## 🔧 Configuración Avanzada

### Variables de Entorno

- `STEAM_USER`: Usuario de Steam
- `STEAM_PASS`: Contraseña de Steam  
- `STEAM_GUARD`: Código Steam Guard (opcional)
- `GAME_SPEED`: Velocidad del juego (default: 16)
- `MOD_URLS`: URLs de mods separadas por comas

### Puertos

- `5900`: VNC Server
- `8000`: API HTTP
- `5555`: ZMQ para comunicación con mods (interno)

## 🎯 Funcionalidades

- ✅ Descarga automática de Balatro via Steam
- ✅ Ejecutor de juegos nativo con Love2D
- ✅ **Lovely Injector integrado para mods**
- ✅ Acceso remoto via VNC
- ✅ API REST para automatización
- ✅ Descarga automática de mods
- ✅ Integración con IA (ZMQ)
- ✅ Persistencia de datos Steam

## ⚠️ Limitaciones

- Balatro debe estar en tu biblioteca de Steam
- Requiere credenciales válidas de Steam
- El rendimiento depende de la extracción correcta del juego para Love2D
- Lovely Injector es obligatorio y se integra automáticamente

## 🔧 Arquitectura Técnica

### Flujo de Ejecución

1. **Descarga**: Steam descarga Balatro.exe
2. **Extracción**: Se extrae el contenido Lua del ejecutable
3. **Lovely Setup**: Se descarga y configura Lovely Injector v0.8.0
4. **Mods**: Se sincronizan mods al directorio `/root/.local/share/Balatro/Mods`
5. **Ejecución**: `LD_PRELOAD=liblovely.so love .` ejecuta el juego con mods

### Integración Love2D + Lovely

- **Método nativo**: No requiere Wine/Proton
- **LD_PRELOAD**: Inyección directa en el proceso Love2D
- **Hook lua functions**: Lovely intercepta `luaL_loadbuffer` para parchar código
- **Directorio estándar**: Compatible con el ecosistema de mods existente

MUY IMPORTANTE: el save del juego está en `/root/.local/share/love/`
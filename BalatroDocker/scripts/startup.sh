#!/bin/bash
# JokerNet startup script
echo "🚀 Starting JokerNet..."

# Temporalmente removemos -e para debugging
set -uo pipefail

echo "🚀 Starting JokerNet...1"
echo "DEBUG: Verificando archivos..."
echo "DEBUG: ¿Existe /usr/local/bin/config_utils.sh? $(test -f /usr/local/bin/config_utils.sh && echo 'SÍ' || echo 'NO')"
echo "DEBUG: ¿Existe /etc/app/paths.env? $(test -f /etc/app/paths.env && echo 'SÍ' || echo 'NO')"
echo "DEBUG: Listando /usr/local/bin/:"
ls -la /usr/local/bin/ || echo "ERROR: No se puede listar /usr/local/bin/"

# Intentar cargar config_utils.sh con manejo de errores
if [[ -f "/usr/local/bin/config_utils.sh" ]]; then
    echo "DEBUG: Cargando config_utils.sh..."
    source "/usr/local/bin/config_utils.sh" || {
        echo "ERROR: Falló al cargar config_utils.sh"
        exit 1
    }
    echo "🚀 Starting JokerNet...2"
else
    echo "ERROR: config_utils.sh no encontrado"
    exit 1
fi

echo "DEBUG: Cargando configuración..."
load_config "/etc/app/paths.env" || {
    echo "ERROR: Falló al cargar configuración"
    exit 1
}

# Setup environment
export DISPLAY=:0 XDG_RUNTIME_DIR=/tmp/runtime-root
mkdir -p "$XDG_RUNTIME_DIR"
modprobe uinput 2>/dev/null || true
chmod 666 /dev/uinput 2>/dev/null || true

# Download game if credentials provided
if [[ -n "${STEAM_USER:-}" && -n "${STEAM_PASS:-}" && ! -f "$STEAM_ROOT/steamapps/appmanifest_2379780.acf" ]]; then
    echo "⬇️ Downloading Balatro..."
    timeout 300 steamcmd +@sSteamCmdForcePlatformType windows +login "$STEAM_USER" "$STEAM_PASS" "${STEAM_GUARD:-}" +app_update 2379780 validate +quit || true
fi

# Setup mods and systems in background
(
    sleep 3
    /usr/local/bin/setup_love.sh 2>/dev/null || true
    /usr/local/bin/setup_all.sh
) &

echo "✅ JokerNet ready - API:$API_PORT VNC:$VNC_PORT"
exec /usr/bin/supervisord -c /config/supervisord.conf
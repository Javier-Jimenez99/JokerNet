#!/bin/bash
# Setup Love2D for Balatro
set -e

source "$(dirname "$0")/config_utils.sh"
load_config "/etc/app/paths.env" 2>/dev/null || true

LOVE_DIR="/opt/balatro-love"

echo "🎮 Setting up Love2D..."

# Extract Balatro.exe if exists
if [[ -f "$BALATRO_STEAM_DIR/Balatro.exe" ]]; then
    mkdir -p "$LOVE_DIR"
    cd "$LOVE_DIR"
    
    # Try extraction methods
    cp "$BALATRO_STEAM_DIR/Balatro.exe" . 
    unzip -q Balatro.exe 2>/dev/null || 7z x Balatro.exe &>/dev/null || {
        # Try LÖVE executable method
        tail -c +1000000 Balatro.exe > temp.zip 2>/dev/null
        unzip -q temp.zip 2>/dev/null && rm temp.zip
    }
    
    # Create wrapper script
    if [[ -f "main.lua" ]]; then
        cat > /usr/local/bin/balatro-lovely <<'EOF'
#!/bin/bash
export DISPLAY=:1
cd /opt/balatro-love
LD_PRELOAD=/opt/lovely/liblovely.so love .
EOF
        chmod +x /usr/local/bin/balatro-lovely
        echo "✅ Love2D setup complete"
    else
        echo "❌ Love2D setup failed"
        exit 1
    fi
else
    echo "⚠️ Balatro.exe not found, skipping Love2D setup"
fi

#!/bin/bash
# Setup all mods and Lovely Injector for JokerNet
set -euo pipefail

source "$(dirname "$0")/config_utils.sh"
load_config "/etc/app/paths.env"
validate_config || exit 1
setup_dirs

echo "🎮 Setting up Balatro mods..."

# Install Lovely Injector
echo "📥 Installing Lovely Injector ${LOVELY_VERSION}..."
mkdir -p "$LOVELY_INSTALL_DIR"
curl -sSL "$LOVELY_DOWNLOAD_URL" | tar -xz -C "$LOVELY_INSTALL_DIR"
[[ ! -f "$LOVELY_INSTALL_DIR/liblovely.so" ]] && { echo "❌ Lovely install failed"; exit 1; }

# Setup mods
echo "📦 Setting up mods..."

# Install Steamodded (SMODS)
echo "📥 Installing Steamodded..."
if [[ ! -d "$LOVELY_MODS_DIR/Steamodded" ]]; then
    git clone --depth 1 https://github.com/Steamodded/smods.git "$LOVELY_MODS_DIR/Steamodded" || {
        echo "⚠️ Git clone failed, trying ZIP method..."
        curl -L -o /tmp/smods.zip https://github.com/Steamodded/smods/archive/refs/heads/main.zip
        unzip -q /tmp/smods.zip -d /tmp
        mv /tmp/smods-main "$LOVELY_MODS_DIR/Steamodded"
        rm -f /tmp/smods.zip
    }
    echo "✅ Steamodded installed"
else
    echo "✅ Steamodded already exists"
fi

# Copy BalatroLogger
[[ -d "$MOD_SOURCE_DIR" ]] && cp -r "$MOD_SOURCE_DIR" "$LOVELY_MODS_DIR/" || { echo "❌ BalatroLogger not found"; exit 1; }

# Download external mods if configured
if [[ -n "${MOD_URLS:-}" ]]; then
    mkdir -p "$BALATRO_STEAM_DIR/Mods" "$TEMP_MODS_DIR"
    echo "$MOD_URLS" | tr ',' '\n' | while read -r url; do
        [[ -z "${url// }" ]] && continue
        url=$(echo "$url" | xargs)
        name=$(basename "$url" .zip)
        dest="$BALATRO_STEAM_DIR/Mods/$name"
        
        if [[ ! -d "$dest" ]]; then
            echo "  Downloading $name..."
            temp_file=$(mktemp -p "$TEMP_MODS_DIR")
            curl -sSL "$url" -o "$temp_file" && unzip -o -q "$temp_file" -d "$BALATRO_STEAM_DIR/Mods" && rm -f "$temp_file"
        fi
    done
    
    # Sync external mods to Lovely
    [[ -d "$BALATRO_STEAM_DIR/Mods" ]] && rsync -a "$BALATRO_STEAM_DIR/Mods/" "$LOVELY_MODS_DIR/" --exclude="BalatroLogger*" 2>/dev/null || true
fi

# Configure environment
echo "LOVELY_MOD_DIR=$LOVELY_MODS_DIR" >> /etc/environment
echo "LOVELY_MODS_DIR=$LOVELY_MODS_DIR" >> /etc/environment

echo "✅ Setup complete - Mods: $(ls -1 "$LOVELY_MODS_DIR" | wc -l) installed"

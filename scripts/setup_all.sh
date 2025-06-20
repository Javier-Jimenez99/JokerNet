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
        
        # Handle Steamodded examples repository specially
        if [[ "$url" == *"Steamodded/examples"* ]]; then
            echo "  📦 Downloading Steamodded examples..."
            temp_file=$(mktemp -p "$TEMP_MODS_DIR")
            temp_dir=$(mktemp -d -p "$TEMP_MODS_DIR")
            
            if curl -sSL "$url" -o "$temp_file" && unzip -q "$temp_file" -d "$temp_dir"; then
                # Extract specific mods from the examples repo
                examples_dir=$(find "$temp_dir" -name "examples-*" -type d | head -1)
                if [[ -d "$examples_dir/Mods/KeyboardController" ]]; then
                    echo "    📁 Installing KeyboardController..."
                    cp -r "$examples_dir/Mods/KeyboardController" "$LOVELY_MODS_DIR/"
                fi
                # Add other specific mods here if needed
            fi
            rm -rf "$temp_file" "$temp_dir"
        else
            # Handle regular mod downloads
            name=$(basename "$url" .zip)
            dest="$BALATRO_STEAM_DIR/Mods/$name"
            
            if [[ ! -d "$dest" ]]; then
                echo "  📁 Downloading $name..."
                temp_file=$(mktemp -p "$TEMP_MODS_DIR")
                curl -sSL "$url" -o "$temp_file" && unzip -o -q "$temp_file" -d "$BALATRO_STEAM_DIR/Mods" && rm -f "$temp_file"
            fi
        fi
    done
    
    # Sync external mods to Lovely
    [[ -d "$BALATRO_STEAM_DIR/Mods" ]] && rsync -a "$BALATRO_STEAM_DIR/Mods/" "$LOVELY_MODS_DIR/" --exclude="BalatroLogger*" 2>/dev/null || true
fi

# Configure environment
echo "LOVELY_MOD_DIR=$LOVELY_MODS_DIR" >> /etc/environment
echo "LOVELY_MODS_DIR=$LOVELY_MODS_DIR" >> /etc/environment

# Setup uinput for virtual input devices
echo "🎮 Setting up uinput for virtual input devices..."

# Check if uinput module is loaded (only if tools are available)
if command -v lsmod >/dev/null 2>&1; then
    if ! lsmod | grep -q uinput; then
        echo "⚠️ uinput module not loaded"
        if command -v modprobe >/dev/null 2>&1; then
            echo "⚠️ Attempting to load uinput module..."
            modprobe uinput 2>/dev/null || echo "⚠️ Could not load uinput module (may need privileged container)"
        else
            echo "⚠️ modprobe not available - relying on host kernel"
        fi
    else
        echo "✅ uinput module is loaded"
    fi
else
    echo "⚠️ lsmod not available - assuming uinput is available from host"
fi

# Check if uinput device exists and set permissions
if [[ -e /dev/uinput ]]; then
    chmod 666 /dev/uinput
    echo "✅ uinput device found and permissions configured"
else
    echo "⚠️ /dev/uinput not found - ensure it's mounted from host"
    echo "⚠️ Run: docker run --device=/dev/uinput:/dev/uinput --privileged"
fi

# Check if /dev/input exists for gamepad detection
if [[ -d /dev/input ]]; then
    echo "✅ /dev/input directory found"
else
    echo "⚠️ /dev/input not found - ensure it's mounted from host"
fi

echo "✅ Setup complete - Mods: $(ls -1 "$LOVELY_MODS_DIR" | wc -l) installed"

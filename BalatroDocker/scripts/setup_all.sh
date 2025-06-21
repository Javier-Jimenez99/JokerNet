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

# Install additional mods from MOD_URLS
if [[ -n "${MOD_URLS:-}" ]]; then
    echo "📥 Installing additional mods from MOD_URLS..."
    IFS=',' read -ra URLS <<< "$MOD_URLS"
    for url in "${URLS[@]}"; do
        url=$(echo "$url" | xargs)  # trim whitespace
        if [[ -n "$url" ]]; then
            echo "📦 Downloading mod from: $url"
            
            # Extract mod name from URL (get the repo name)
            if [[ "$url" =~ github\.com/[^/]+/([^/]+) ]]; then
                mod_name="${BASH_REMATCH[1]}"
                # Remove common suffixes
                mod_name="${mod_name%.git}"
                mod_name="${mod_name%-main}"
                mod_name="${mod_name%-master}"
            else
                # Fallback: use timestamp if we can't extract name
                mod_name="mod_$(date +%s)"
            fi
            
            echo "📂 Installing mod as: $mod_name"
            
            # Download and extract mod
            temp_file="/tmp/${mod_name}.zip"
            if curl -L -o "$temp_file" "$url"; then
                # Extract to temporary directory first
                temp_dir="/tmp/extract_${mod_name}"
                mkdir -p "$temp_dir"
                
                if unzip -q "$temp_file" -d "$temp_dir"; then
                    # Find the actual mod directory (usually the first subdirectory)
                    extracted_dir=$(find "$temp_dir" -mindepth 1 -maxdepth 1 -type d | head -n1)
                    
                    if [[ -n "$extracted_dir" && -d "$extracted_dir" ]]; then
                        # Move to mods directory
                        target_dir="$LOVELY_MODS_DIR/$mod_name"
                        mv "$extracted_dir" "$target_dir"
                        echo "✅ $mod_name installed successfully"
                    else
                        echo "⚠️ Could not find extracted directory for $mod_name"
                    fi
                else
                    echo "⚠️ Failed to extract $mod_name"
                fi
                
                # Cleanup
                rm -f "$temp_file"
                rm -rf "$temp_dir"
            else
                echo "⚠️ Failed to download mod from $url"
            fi
        fi
    done
else
    echo "ℹ️ No additional mods specified in MOD_URLS"
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

#!/bin/bash
# Config utilities for JokerNet

load_config() {
    local config_file="${1:-/etc/app/paths.env}"
    
    if [[ ! -f "$config_file" ]]; then
        echo "❌ Config not found: $config_file"
        return 1
    fi
    
    set -a
    source "$config_file"
    set +a
    
    # Auto-derive paths
    export BALATRO_STEAM_DIR="${STEAM_ROOT}/steamapps/common/Balatro"
    export LOVELY_MODS_DIR="${USER_DATA_DIR}/Mods"
    export LOVELY_INSTALL_DIR="/opt/lovely"
    export LOVELY_DOWNLOAD_URL="https://github.com/ethangreen-dev/lovely-injector/releases/download/${LOVELY_VERSION}/lovely-x86_64-unknown-linux-gnu.tar.gz"
    export BALATRO_CMD="LD_PRELOAD=${LOVELY_INSTALL_DIR}/liblovely.so love ${BALATRO_STEAM_DIR}"
    export API_URL="http://localhost:${API_PORT}"
    export TEMP_MODS_DIR="/tmp/mods"
}

validate_config() {
    local required=(STEAM_ROOT USER_DATA_DIR MOD_SOURCE_DIR LOVELY_VERSION API_PORT)
    for var in "${required[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo "❌ Missing: $var"
            return 1
        fi
    done
    return 0
}

setup_dirs() {
    mkdir -p "$LOVELY_MODS_DIR" "$TEMP_MODS_DIR" "/var/log/supervisor" "/etc/app"
}

# Auto-load if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    load_config "$1"
    validate_config
    setup_dirs
fi

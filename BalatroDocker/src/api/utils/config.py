"""
Configuration utilities for the Balatro game control system.
"""
import os
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment file and derive auto-paths.
    
    Returns:
        Dict[str, Any]: Configuration dictionary with all required paths
    """
    config = {}
    config_file = "/etc/app/paths.env"
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = os.path.expandvars(value.strip('"'))
                    config[key] = value
    
    # Auto-derive paths based on configuration
    steam_root = config.get('STEAM_ROOT', '/root/.local/share/Steam')
    user_data_dir = config.get('USER_DATA_DIR', '/root/.local/share/Balatro')
    lovely_install_dir = '/opt/lovely'
    balatro_love_dir = '/opt/balatro-love'
    
    config.update({
        'BALATRO_STEAM_DIR': f"{steam_root}/steamapps/common/Balatro",
        'BALATRO_LOVE_DIR': balatro_love_dir,
        'LOVELY_MODS_DIR': f"{user_data_dir}/Mods",
        'LOVELY_INSTALL_DIR': lovely_install_dir,
        'BALATRO_CMD': 'love .',
        'LOVELY_PRELOAD': f"{lovely_install_dir}/liblovely.so"
    })
    
    return config


def get_config() -> Dict[str, Any]:
    """
    Get the configuration for the Balatro game control system.
    
    Returns:
        Dict[str, Any]: Configuration dictionary with all required paths
    """
    return load_config()

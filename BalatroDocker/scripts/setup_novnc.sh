#!/bin/bash

# Script para configurar noVNC con configuraciones optimizadas
# Este script se ejecuta durante la construcción del Docker

set -e

echo "Configurando noVNC..."

# Crear directorio de configuración personalizada
mkdir -p /opt/noVNC/app/ui

# Configuración personalizada de noVNC para Balatro
cat > /opt/noVNC/app/ui/ui.js << 'EOF'
// Configuración personalizada para Balatro
(function() {
    'use strict';
    
    // Configuración automática al cargar
    window.addEventListener('load', function() {
        // Auto-conectar después de un breve delay
        setTimeout(function() {
            if (typeof UI !== 'undefined' && UI.connect) {
                try {
                    UI.connect();
                } catch (e) {
                    console.log('Auto-connect attempt:', e);
                }
            }
        }, 1000);
        
        // Configurar calidad y compresión para gaming
        if (typeof UI !== 'undefined' && UI.rfb) {
            try {
                UI.rfb.qualityLevel = 9;
                UI.rfb.compressionLevel = 2;
            } catch (e) {
                console.log('Quality settings:', e);
            }
        }
    });
})();
EOF

# Configuración CSS personalizada para mejor experiencia
cat > /opt/noVNC/app/styles/balatro.css << 'EOF'
/* Estilos personalizados para Balatro */
body {
    margin: 0;
    padding: 0;
    background: #1a1a2e;
    font-family: 'Arial', sans-serif;
}

#noVNC_container {
    background: #16213e;
}

.noVNC_status {
    background: rgba(26, 26, 46, 0.9) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

#noVNC_control_bar {
    background: rgba(26, 26, 46, 0.95) !important;
    border-radius: 8px 8px 0 0 !important;
}

.noVNC_button {
    background: #16213e !important;
    border: 1px solid #4a5568 !important;
    color: #ffffff !important;
    border-radius: 4px !important;
}

.noVNC_button:hover {
    background: #2d3748 !important;
    border-color: #63b3ed !important;
}

#noVNC_screen {
    border-radius: 0 0 8px 8px !important;
}
EOF

echo "noVNC configurado correctamente."

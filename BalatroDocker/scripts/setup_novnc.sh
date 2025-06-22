#!/bin/bash
# Script simple para configurar noVNC
set -e

echo "Configurando noVNC básico..."

# Solo CSS simple para ocultar elementos innecesarios
cat > /opt/noVNC/app/styles/balatro.css << 'EOF'
/* CSS mínimo para noVNC */
#noVNC_control_bar {
    display: none !important;
}

body {
    margin: 0 !important;
    padding: 0 !important;
    background: #000000 !important;
}

#noVNC_container {
    background: #000000 !important;
}
EOF

echo "noVNC configurado correctamente."

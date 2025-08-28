#!/bin/bash

# Script para iniciar JokerNet con detección automática de GPU
echo "🃏 Iniciando JokerNet..."

# Detectar si hay GPU NVIDIA disponible
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    export NVIDIA_VISIBLE_DEVICES=all
    export NVIDIA_DRIVER_CAPABILITIES=compute,utility
    export GPU_DEVICES='[{"driver": "nvidia", "count": "all", "capabilities": ["gpu"]}]'
    echo "🎮 GPU NVIDIA detectada - Habilitando aceleración GPU"
else
    export NVIDIA_VISIBLE_DEVICES=""
    export NVIDIA_DRIVER_CAPABILITIES=""
    export GPU_DEVICES="[]"
    echo "💻 No se detectó GPU NVIDIA - Usando CPU"
fi

# Cargar módulo uinput
sudo modprobe uinput
sudo chmod 666 /dev/uinput

# Levantar Docker
cd BalatroDocker

# Usar profile apropiado según GPU
if [[ "${NVIDIA_VISIBLE_DEVICES}" == "all" ]]; then
    echo "🚀 Iniciando con soporte GPU..."
    docker compose --profile gpu up balatro-gpu --build -d
else
    echo "🚀 Iniciando en modo CPU..."
    docker compose up balatro --build -d
fi

cd ..

# Esperar 10 segundos para que Docker se levante
sleep 10

# Ejecutar Streamlit (los logs aparecerán aquí)
uv run streamlit run src/app.py --server.port 8501

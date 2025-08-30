#!/bin/bash


# Script to start JokerNet with automatic GPU detection
echo "🃏 Starting JokerNet..."

# Detect if an NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    export NVIDIA_VISIBLE_DEVICES=all
    export NVIDIA_DRIVER_CAPABILITIES=compute,utility
    export GPU_DEVICES='[{"driver": "nvidia", "count": "all", "capabilities": ["gpu"]}]'
    echo "🎮 NVIDIA GPU detected - Enabling GPU acceleration"
else
    export NVIDIA_VISIBLE_DEVICES=""
    export NVIDIA_DRIVER_CAPABILITIES=""
    export GPU_DEVICES="[]"
    echo "💻 No NVIDIA GPU detected - Using CPU"
fi

# Load uinput module
sudo modprobe uinput
sudo chmod 666 /dev/uinput

# Start Docker
cd BalatroDocker

# Use appropriate profile depending on GPU
if [[ "${NVIDIA_VISIBLE_DEVICES}" == "all" ]]; then
    echo "🚀 Starting with GPU support..."
    docker compose --profile gpu up balatro-gpu --build -d
else
    echo "🚀 Starting in CPU mode..."
    docker compose up balatro --build -d
fi


cd ..

# Wait 10 seconds for Docker to start
sleep 10

# Run Streamlit (logs will appear here)
uv run streamlit run src/app.py --server.port 8501

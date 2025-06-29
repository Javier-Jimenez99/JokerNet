#!/bin/bash

# Script simple para iniciar JokerNet
echo "🃏 Iniciando JokerNet..."

# Cargar módulo uinput
sudo modprobe uinput
sudo chmod 666 /dev/uinput

# Levantar Docker
cd BalatroDocker
docker compose up --build -d
cd ..

# Esperar 10 segundos para que Docker se levante
sleep 10

# Ejecutar Streamlit (los logs aparecerán aquí)
streamlit run src/streamlit_app.py --server.port 8501

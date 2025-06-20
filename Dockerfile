FROM steamcmd/steamcmd:ubuntu

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    GAME_SPEED=16

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    curl \
    unzip \
    git \
    xvfb \
    x11vnc \
    file \
    software-properties-common \
    supervisor \
    bsdmainutils \
    p7zip-full \
    fluxbox \
    rsync

# Instalar Love2D y luasocket para mods
RUN add-apt-repository ppa:bartbes/love-stable -y && \
    apt-get update && \
    apt-get install -y love lua-socket

# Instalar dependencias mínimas para SDL
RUN apt-get install -y libsdl2-2.0-0

# Crear usuario steam si no existe
RUN if ! id steam &>/dev/null; then useradd -m -s /bin/bash steam; fi

# API Python - instalar dependencias
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# Copiar configuración centralizada
COPY config/paths.env /etc/app/paths.env

# Scripts
COPY scripts/config_utils.sh /usr/local/bin/config_utils.sh
COPY scripts/setup_all.sh /usr/local/bin/setup_all.sh
COPY scripts/startup.sh /usr/local/bin/startup.sh
COPY scripts/setup_love.sh /usr/local/bin/setup_love.sh
COPY config/supervisord.conf /config/supervisord.conf

# Hacer scripts ejecutables
RUN chmod +x /usr/local/bin/*.sh
RUN chmod +x /usr/local/bin/*.sh

# Copiar el mod BalatroLogger
COPY BalatroLogger /BalatroLogger

# Crear directorios necesarios
RUN mkdir -p /tmp/.X11-unix /var/log/supervisor /root/.local/share \
    && chmod 1777 /tmp/.X11-unix

# Copiar configuración de Love2D guardada
COPY data/save_state /root/.local/share/love

# FastAPI
COPY api /srv/api
WORKDIR /srv/api

# Usar script de startup
ENTRYPOINT ["/usr/local/bin/startup.sh"]

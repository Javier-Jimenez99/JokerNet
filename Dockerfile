FROM steamcmd/steamcmd:ubuntu

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    GAME_SPEED=16

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
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
    rsync \
    libudev-dev \
    build-essential \
    wmctrl \
    x11-utils \
    kmod \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Install Love2D and luasocket for mods
RUN add-apt-repository ppa:bartbes/love-stable -y && \
    apt-get update && \
    apt-get install -y love lua-socket

# Create steam user if not exists
RUN if ! id steam &>/dev/null; then useradd -m -s /bin/bash steam; fi

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# Copy configuration
COPY config/paths.env /etc/app/paths.env

# Copy essential scripts
COPY scripts/config_utils.sh /usr/local/bin/config_utils.sh
COPY scripts/setup_all.sh /usr/local/bin/setup_all.sh
COPY scripts/startup.sh /usr/local/bin/startup.sh
COPY scripts/setup_love.sh /usr/local/bin/setup_love.sh
COPY config/supervisord.conf /config/supervisord.conf

# Make scripts executable
RUN chmod +x /usr/local/bin/*.sh

# Copy Auto Start Game mod
COPY BalatroLogger /BalatroLogger

# Create necessary directories
RUN mkdir -p /tmp/.X11-unix /var/log/supervisor /root/.local/share \
    && chmod 1777 /tmp/.X11-unix

# Copy Love2D saved configuration
COPY data/save_state /root/.local/share/love

# Copy minimal FastAPI
COPY api /srv/api
WORKDIR /srv/api

# Use startup script
ENTRYPOINT ["/usr/local/bin/startup.sh"]

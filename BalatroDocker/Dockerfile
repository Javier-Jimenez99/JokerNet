FROM steamcmd/steamcmd:ubuntu

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:0 \
    GAME_SPEED=16 \
    HF_HOME=/root/.cache/huggingface \
    TRANSFORMERS_CACHE=/root/.cache/huggingface \
    HF_HUB_CACHE=/root/.cache/huggingface/hub \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=all

# Add NVIDIA package repositories with retry logic
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    && for i in 1 2 3; do \
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb && break || sleep 10; \
    done \
    && dpkg -i cuda-keyring_1.0-1_all.deb \
    && (apt-get update || true) \
    && sleep 5 \
    && apt-get update

# Install basic system dependencies first
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-tk \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install GUI and system tools
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    file \
    software-properties-common \
    supervisor \
    bsdmainutils \
    p7zip-full \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Install development and multimedia tools
RUN apt-get update && apt-get install -y \
    libudev-dev \
    build-essential \
    wmctrl \
    x11-utils \
    xdotool \
    kmod \
    imagemagick \
    nodejs \
    npm \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Try to install CUDA runtime (optional)
RUN apt-get update && \
    (apt-get install -y cuda-runtime-11-8 || echo "CUDA installation failed, continuing without CUDA") && \
    rm -rf /var/lib/apt/lists/*

# Install Love2D and luasocket for mods
RUN add-apt-repository ppa:bartbes/love-stable -y && \
    apt-get update && \
    apt-get install -y love lua-socket

# Create steam user if not exists
RUN if ! id steam &>/dev/null; then useradd -m -s /bin/bash steam; fi

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# Install noVNC and websockify
RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC && \
    pip3 install --break-system-packages websockify

# Copy configuration
COPY config/paths.env /etc/app/paths.env
COPY config/nginx.conf /etc/nginx/sites-available/default

# Copy essential scripts
COPY scripts/config_utils.sh /usr/local/bin/config_utils.sh
COPY scripts/setup_all.sh /usr/local/bin/setup_all.sh
COPY scripts/startup.sh /usr/local/bin/startup.sh
COPY scripts/setup_love.sh /usr/local/bin/setup_love.sh
COPY scripts/setup_novnc.sh /usr/local/bin/setup_novnc.sh
COPY config/supervisord.conf /config/supervisord.conf

# Make scripts executable
RUN chmod +x /usr/local/bin/*.sh

# Configure noVNC
RUN /usr/local/bin/setup_novnc.sh

# Copy Auto Start Game mod
COPY BalatroLogger /BalatroLogger

# Create necessary directories
RUN mkdir -p /tmp/.X11-unix /var/log/supervisor /root/.local/share /root/.cache/huggingface \
    && chmod 1777 /tmp/.X11-unix

# Copy Love2D saved configuration
COPY data/save_state /root/.local/share/love

# Copy src directory with API and MCP server
COPY src /srv/src
WORKDIR /srv/src

# Use startup script
ENTRYPOINT ["/usr/local/bin/startup.sh"]

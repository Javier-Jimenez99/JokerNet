import streamlit as st
from streamlit.components.v1 import iframe   # 1 solo iframe, sin sandbox extra

st.set_page_config(layout="wide", page_title="Balatro - Escritorio Remoto")
st.title("🃏 Balatro - Escritorio Remoto")

# Configuración de conexión noVNC
host = "localhost"  # Cambia esto por tu IP/dominio si ejecutas remotamente
ws_port = "6080"

novnc_url = (
    "http://localhost:6080/vnc.html?host=localhost&port=6080&autoconnect=1&resize=scale&reconnect=1"
)

# Información de conexión
st.info("""
🎮 **Balatro está funcionando en el escritorio remoto**
- Usa el mouse y teclado normalmente
- La conexión se establece automáticamente
- Resolución: 1920x1080
""")

# Iframe con noVNC
iframe(src=novnc_url, height=800, scrolling=False)   # aquí se pinta la consola

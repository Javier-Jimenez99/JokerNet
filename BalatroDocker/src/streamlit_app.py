import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="wide", page_title="Balatro - Escritorio Remoto")
st.title("🃏 Balatro - Escritorio Remoto")

# Configuración de conexión noVNC
host = "localhost"  # Dentro del Docker todo corre en localhost
ws_port = "6080"

novnc_url = (
    f"http://{host}:{ws_port}/vnc.html"
    f"?host={host}&port={ws_port}&autoconnect=1&resize=scale&reconnect=1"
)

# Información de conexión
st.info("""
🎮 **Balatro está funcionando en el escritorio remoto**
- Usa el mouse y teclado normalmente
- La conexión se establece automáticamente
- Resolución: 1920x1080
""")

# Iframe con noVNC
html(
    f'''
    <iframe 
        src="{novnc_url}" 
        style="
            width:100%;
            height:800px;
            border:none;
            border-radius:8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        "
        allow="fullscreen"
    ></iframe>
    ''',
    height=800,
)

# Instrucciones adicionales
st.markdown("""
### 📋 Instrucciones:
1. **Balatro** se ejecuta automáticamente al iniciar el contenedor
2. Puedes interactuar con el escritorio usando mouse y teclado
3. Si necesitas reconectar, recarga la página
4. Para pantalla completa, usa el botón en la barra de herramientas de noVNC

### 🔧 APIs disponibles:
- **API REST**: `http://localhost:8000/docs`
- **MCP Server**: Puerto configurado automáticamente
- **noVNC**: `http://localhost:6080`
""")

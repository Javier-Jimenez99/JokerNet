import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="wide", page_title="Balatro – Escritorio Remoto")
st.title("🃏 Balatro – Escritorio Remoto")

novnc_url = "http://localhost:6080/vnc.html" \
            "?autoconnect=1&resize=scale&view_clip=1&reconnect=1"

html(f'<iframe src="{novnc_url}" style="width:100%;height:800px;border:none;"></iframe>',
     height=820)

st.info("🎮 **Balatro** corriendo en el escritorio remoto…")

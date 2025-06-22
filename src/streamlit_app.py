import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="wide", page_title="Balatro – Escritorio Remoto")
st.title("🃏 Balatro – Escritorio Remoto")

novnc_url = (
    "http://localhost:6080/vnc.html"
    "?autoconnect=1"
    "&reconnect=1"
    "&resize=scale"      # ← encoge o agranda el framebuffer
)

columns = st.columns(2)
with columns[0]:
    st.markdown(
        "### Balatro es un juego de cartas de rol y estrategia, "
        "donde los jugadores deben construir mazos y enfrentarse a enemigos en un mundo de fantasía."
    )
    st.markdown(
        "Para jugar, simplemente haz clic en el botón de abajo para abrir el escritorio remoto."
    )
with columns[1]:
     html(f'<iframe src="{novnc_url}" style="border:none;height:100vh;width:100%" allowfullscreen></iframe>',height=820)

st.info("🎮 **Balatro** corriendo en el escritorio remoto…")

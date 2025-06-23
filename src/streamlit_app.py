import streamlit as st
from streamlit.components.v1 import html
import requests

def start_balatro():
     """Start the Balatro game in a remote desktop environment."""
     res = requests.post("http://localhost:8000/start_balatro")

     if res.status_code != 200:
          st.error("Failed to start Balatro game. Please check the server logs.")

def start_game(deck="b_blue", stake=1):
     """Start the game when the button is clicked."""
     start_balatro()
     res = requests.post("http://localhost:8000/auto_start", json={"deck": deck, "stake": stake})
     if res.status_code != 200:
          st.error("Failed to start the game. Please check the server logs.")

st.set_page_config(layout="wide", page_title="Balatro – Escritorio Remoto")
start_balatro()
st.title("🃏 Balatro – Escritorio Remoto")

novnc_url = (
    "http://localhost:6080/vnc.html"
    "?autoconnect=1"
    "&reconnect=1"
    "&resize=scale"      # ← encoge o agranda el framebuffer
)

columns = st.columns(2)
with columns[0]:

     with st.expander("Start New Game", expanded=False):
          with st.form("start_game_form"):
               deck = st.selectbox(
                    "Selecciona el mazo:",
                    [
                              "b_red",       # Mazo Rojo (predeterminado)
                              "b_blue",      # Mazo Azul
                              "b_yellow",    # Mazo Amarillo
                              "b_green",     # Mazo Verde
                              "b_black",     # Mazo Negro
                              "b_magic",     # Mazo Mágico
                              "b_nebula",    # Mazo Nebulosa
                              "b_ghost",     # Mazo Fantasma
                              "b_abandoned", # Mazo Abandonado
                              "b_checkered", # Mazo A Cuadros
                              "b_zodiac",    # Mazo Zodíaco
                              "b_painted",   # Mazo Pintado
                              "b_anaglyph",  # Mazo Anaglifo
                              "b_plasma",    # Mazo Plasma
                              "b_erratic"    # Mazo Errático
                    ],
                    index=0,
                    format_func=lambda x: {
                              "b_red": "Mazo Rojo (predeterminado)",
                              "b_blue": "Mazo Azul",
                              "b_yellow": "Mazo Amarillo",
                              "b_green": "Mazo Verde",
                              "b_black": "Mazo Negro",
                              "b_magic": "Mazo Mágico",
                              "b_nebula": "Mazo Nebulosa",
                              "b_ghost": "Mazo Fantasma",
                              "b_abandoned": "Mazo Abandonado",
                              "b_checkered": "Mazo A Cuadros",
                              "b_zodiac": "Mazo Zodíaco",
                              "b_painted": "Mazo Pintado",
                              "b_anaglyph": "Mazo Anaglifo",
                              "b_plasma": "Mazo Plasma",
                              "b_erratic": "Mazo Errático"
                    }.get(x, x)
               )
               stake = st.slider("Selecciona la dificultad:", 1, 8, 1)
               start_button = st.form_submit_button("Iniciar juego")
               
               if start_button:
                    start_game(deck, stake)

with columns[1]:
     html(f'<iframe src="{novnc_url}" style="border:none;height:100vh;width:100%" allowfullscreen></iframe>',height=820)

st.info("🎮 **Balatro** corriendo en el escritorio remoto…")

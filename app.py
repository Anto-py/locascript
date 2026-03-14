import socket
import subprocess
import sys
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ui.theme import inject_theme
from ui import file_tab, live_tab


def _display_server_running(port=8502) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def _launch_display_server():
    if not _display_server_running():
        display_path = str(__import__("pathlib").Path(__file__).parent / "display.py")
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", display_path,
             "--server.port", "8502", "--server.headless", "true"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


_launch_display_server()

st.set_page_config(
    page_title="Locascript",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_theme()

st.title("🎙️ Locascript")
st.caption("Transcription locale — 100% sur votre machine, 0€, open source")

tab_file, tab_live = st.tabs(["📁 Fichier", "🔴 En direct"])

with tab_file:
    file_tab.render()

with tab_live:
    live_tab.render()

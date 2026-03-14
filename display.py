"""
Fenêtre d'affichage plein-écran de la transcription en direct.
Lancer avec : streamlit run display.py --server.port 8502
"""
import json
import time
import os
import streamlit as st

LIVE_STATE_FILE = "/tmp/locascript_live.json"

st.set_page_config(
    page_title="Locascript — Affichage",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS plein écran, responsive, texte centré
st.markdown("""
<style>
/* Masquer tout le chrome Streamlit */
#MainMenu, header, footer, .stDeployButton { display: none !important; }
.stAppDeployButton { display: none !important; }

/* Fond noir, texte blanc large */
.stApp {
    background: #0D1617 !important;
}
.block-container {
    padding: 2rem 3rem !important;
    max-width: 100% !important;
    background: transparent !important;
    border: none !important;
}

/* Zone de texte principale */
#transcript-box {
    font-family: 'Inter', system-ui, sans-serif;
    font-size: clamp(1.4rem, 3vw, 2.8rem);
    line-height: 1.6;
    color: #F2EFE6;
    word-wrap: break-word;
}

/* Indicateur enregistrement */
#rec-indicator {
    font-size: 0.9rem;
    color: #E4632E;
    font-weight: 700;
    letter-spacing: 0.1em;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
}
#rec-indicator.stopped {
    color: #127676;
}
</style>
""", unsafe_allow_html=True)


def load_state():
    if not os.path.exists(LIVE_STATE_FILE):
        return None
    try:
        with open(LIVE_STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return None


state = load_state()

if state is None:
    st.markdown(
        '<div id="rec-indicator" class="stopped">○ EN ATTENTE</div>'
        '<div id="transcript-box" style="color:#127676">En attente de la transcription…</div>',
        unsafe_allow_html=True,
    )
else:
    running = state.get("running", False)
    segments = state.get("segments", [])
    has_translation = state.get("has_translation", False)

    indicator = (
        '<div id="rec-indicator">● ENREGISTREMENT EN COURS</div>'
        if running else
        '<div id="rec-indicator" class="stopped">○ ARRÊTÉ</div>'
    )

    lines = []
    for seg in segments:
        text = seg.get("translation", "").strip() if has_translation else seg.get("text", "").strip()
        if text:
            lines.append(text)

    # Afficher les 5 dernières lignes pour rester lisible
    display_text = "<br><br>".join(lines[-5:]) if lines else "…"

    st.markdown(
        f'{indicator}<div id="transcript-box">{display_text}</div>',
        unsafe_allow_html=True,
    )

# Auto-refresh toutes les secondes
time.sleep(1)
st.rerun()

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

st.markdown("""
<style>
#MainMenu, header, footer, .stDeployButton, .stAppDeployButton { display: none !important; }

.stApp { background: #0D1617 !important; }

.block-container {
    padding: 2rem 3rem !important;
    max-width: 100% !important;
    background: transparent !important;
    border: none !important;
}

#rec-indicator {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    color: #E4632E;
}
#rec-indicator.stopped { color: #F2EFE6; }

.transcript-block {
    font-family: 'Inter', system-ui, sans-serif;
    font-size: clamp(1.2rem, 2.5vw, 2.4rem);
    line-height: 1.7;
    color: rgba(242, 239, 230, 0.65);
    display: block;
    margin-bottom: 1.4em;   /* ligne vide entre groupes */
}

.transcript-block.latest {
    color: #F2EFE6;
    background: rgba(228, 99, 46, 0.15);
    border-left: 4px solid #E4632E;
    padding: 0.2em 0.6em;
    border-radius: 4px;
    margin-bottom: 1.4em;
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
        '<div class="transcript-block">En attente de la transcription…</div>',
        unsafe_allow_html=True,
    )
else:
    running = state.get("running", False)
    groups = state.get("groups", [])

    indicator = (
        '<div id="rec-indicator">● ENREGISTREMENT EN COURS</div>'
        if running else
        '<div id="rec-indicator" class="stopped">○ ARRÊTÉ</div>'
    )

    if not groups:
        body = '<div class="transcript-block">En attente de la parole…</div>'
    else:
        parts = []
        for i, group in enumerate(groups):
            text = group.get("text", "").strip()
            if not text:
                continue
            is_last = (i == len(groups) - 1)
            cls = "transcript-block latest" if is_last else "transcript-block"
            parts.append(f'<div class="{cls}">{text}</div>')
        body = "\n".join(parts)

    st.markdown(f"{indicator}{body}", unsafe_allow_html=True)

time.sleep(1)
st.rerun()

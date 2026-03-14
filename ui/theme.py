import streamlit as st

RETRO_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=Inter:wght@400;500&display=swap');

:root {
  --retro-teal:   #127676;
  --retro-orange: #E4632E;
  --retro-jaune:  #E3A535;
  --retro-ink:    #0D1617;
  --retro-paper:  #F2EFE6;
}

.stApp {
  background-color: var(--retro-ink);
}

.block-container {
  background: var(--retro-paper);
  border: 4px solid var(--retro-orange);
  border-radius: 16px;
  padding: 2rem;
}

h1, h2, h3 {
  font-family: 'Oswald', sans-serif;
  color: var(--retro-teal);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.stTabs [data-baseweb="tab"] {
  background-color: var(--retro-ink);
  color: var(--retro-paper);
  border: 2px solid var(--retro-teal);
  border-radius: 8px 8px 0 0;
  font-family: 'Oswald', sans-serif;
  text-transform: uppercase;
}
.stTabs [aria-selected="true"] {
  background-color: var(--retro-teal);
  color: var(--retro-paper);
}

.stButton > button {
  background: var(--retro-jaune);
  color: var(--retro-ink);
  border: 3px solid var(--retro-teal);
  border-radius: 50px;
  font-family: 'Oswald', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.5rem 2rem;
}
.stButton > button:hover {
  background: var(--retro-orange);
  color: var(--retro-paper);
}

.stProgress > div > div {
  background: linear-gradient(90deg, var(--retro-teal), var(--retro-orange), var(--retro-jaune));
}

.stSelectbox label, .stFileUploader label, .stRadio label, .stCheckbox label {
  font-family: 'Inter', sans-serif;
  color: var(--retro-ink);
}

.stAlert {
  border-radius: 8px;
}

/* Indicateur d'enregistrement */
.recording-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--retro-orange);
  animation: pulse 1s infinite;
  margin-right: 8px;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

/* Segments de transcription */
.speaker-a { color: #127676; font-weight: 600; }
.speaker-b { color: #E4632E; font-weight: 600; }
.speaker-c { color: #E3A535; font-weight: 600; }

.transcript-segment {
  font-family: 'Inter', sans-serif;
  padding: 0.4rem 0;
  border-bottom: 1px solid rgba(18, 118, 118, 0.15);
  line-height: 1.6;
}

.timestamp {
  font-family: 'Oswald', sans-serif;
  font-size: 0.8em;
  color: var(--retro-teal);
  opacity: 0.7;
  margin-right: 0.5em;
}
</style>
"""

SPEAKER_COLORS = {
    0: ("#127676", "🟦"),
    1: ("#E4632E", "🟧"),
    2: ("#E3A535", "🟨"),
}

def inject_theme():
    st.markdown(RETRO_CSS, unsafe_allow_html=True)

def speaker_color(speaker_label: str) -> tuple[str, str]:
    """Retourne (couleur_hex, emoji) pour un label locuteur."""
    digits = "".join(c for c in speaker_label if c.isdigit())
    idx = int(digits) % len(SPEAKER_COLORS) if digits else 0
    return SPEAKER_COLORS[idx]

def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def render_segment(seg: dict):
    """Affiche un segment de transcription avec couleur locuteur."""
    ts = format_timestamp(seg.get("start", 0))
    speaker = seg.get("speaker", "")
    text = seg.get("text", "").strip()

    if speaker and speaker != "?":
        color, emoji = speaker_color(speaker)
        label = f'<span style="color:{color};font-weight:700">{emoji} {speaker.upper()}</span>'
    else:
        label = ""

    ts_html = f'<span class="timestamp">[{ts}]</span>'
    st.markdown(
        f'<div class="transcript-segment">{ts_html} {label} {text}</div>',
        unsafe_allow_html=True
    )

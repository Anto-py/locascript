import base64
import pathlib
import streamlit as st

def _bg_base64() -> str:
    img = pathlib.Path(__file__).parent.parent / "background.jpg"
    return base64.b64encode(img.read_bytes()).decode()

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
  background-image: url("data:image/jpeg;base64,{BG}");
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

.block-container {
  background: var(--retro-paper);
  border: 4px solid var(--retro-orange);
  border-radius: 16px;
  padding: 2rem;
  max-width: 860px !important;
  margin-left: auto !important;
  margin-right: auto !important;
  margin-top: 1rem !important;
  margin-bottom: 2rem !important;
}

h1, h2, h3 {
  font-family: 'Oswald', sans-serif;
  color: var(--retro-paper);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
/* À l'intérieur du block-container (fond papier), les titres passent en teal */
.block-container h1,
.block-container h2,
.block-container h3 {
  color: var(--retro-teal);
}
/* Caption sous le titre principal (sur fond sombre) */
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] * {
  color: rgba(242, 239, 230, 0.65) !important;
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
  color: var(--retro-ink);
}

.stProgress > div > div {
  background: linear-gradient(90deg, var(--retro-teal), var(--retro-orange), var(--retro-jaune));
}

.stSelectbox label, .stFileUploader label, .stRadio label, .stCheckbox label,
.stSlider label, .stTextInput label, .stNumberInput label {
  font-family: 'Inter', sans-serif;
  color: var(--retro-ink);
}

/* Contrôles de formulaire : selectbox, text input, number input, slider */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stSelectbox > div > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {
  background: var(--retro-paper) !important;
  background-color: var(--retro-paper) !important;
  color: var(--retro-ink) !important;
  border-color: var(--retro-teal) !important;
}
[data-baseweb="select"] > div {
  border: 1px solid var(--retro-teal) !important;
  border-radius: 8px !important;
}
/* Texte sélectionné dans les selectbox */
[data-baseweb="select"] span,
[data-baseweb="select"] div[data-baseweb="select-value"] {
  color: var(--retro-ink) !important;
}
/* Flèche du selectbox */
[data-baseweb="select"] svg {
  color: var(--retro-teal) !important;
}
/* File uploader */
.stFileUploader > div {
  background: var(--retro-paper) !important;
  border-color: var(--retro-teal) !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background: var(--retro-paper) !important;
  color: var(--retro-ink) !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] button,
.stFileUploader button {
  background: var(--retro-jaune) !important;
  color: var(--retro-ink) !important;
  border: 2px solid var(--retro-teal) !important;
  border-radius: 50px !important;
  font-family: 'Oswald', sans-serif !important;
  text-transform: uppercase !important;
}
/* Slider */
.stSlider > div > div > div {
  color: var(--retro-ink) !important;
}
/* Toggle / checkbox / radio labels */
.stCheckbox span, .stRadio span, .stToggle span {
  color: var(--retro-ink) !important;
}

.stAlert {
  border-radius: 8px;
}

/* Popovers, menus déroulants, tooltips (rendus hors .block-container) */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] > div > div {
  background: var(--retro-paper) !important;
  background-color: var(--retro-paper) !important;
  border-color: var(--retro-teal) !important;
}
[data-baseweb="popover"] {
  border: 2px solid var(--retro-teal) !important;
  border-radius: 8px !important;
}
[data-baseweb="menu"],
[data-baseweb="menu"] > div,
ul[role="listbox"],
ul[role="listbox"] > div {
  background: var(--retro-paper) !important;
  background-color: var(--retro-paper) !important;
}
[data-baseweb="menu"] li,
ul[role="listbox"] li,
li[role="option"] {
  background: var(--retro-paper) !important;
  background-color: var(--retro-paper) !important;
  color: var(--retro-ink) !important;
}
[data-baseweb="menu"] li:hover,
ul[role="listbox"] li:hover,
li[role="option"]:hover {
  background: rgba(18, 118, 118, 0.12) !important;
  background-color: rgba(18, 118, 118, 0.12) !important;
}
[data-baseweb="menu"] li[aria-selected="true"],
li[role="option"][aria-selected="true"] {
  background: rgba(18, 118, 118, 0.2) !important;
  background-color: rgba(18, 118, 118, 0.2) !important;
}
/* Champ de recherche dans les selectbox */
[data-baseweb="popover"] input,
[data-baseweb="select"] input {
  background: var(--retro-paper) !important;
  background-color: var(--retro-paper) !important;
  color: var(--retro-ink) !important;
}

/* Tooltips */
[data-baseweb="tooltip"],
[data-baseweb="tooltip"] > div {
  background: var(--retro-ink) !important;
  background-color: var(--retro-ink) !important;
  color: var(--retro-paper) !important;
}

/* Modals / dialogs */
[data-baseweb="modal"] [data-baseweb="modal-body"] {
  background: var(--retro-paper) !important;
  color: var(--retro-ink) !important;
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
.speaker-b { color: #AD4117; font-weight: 600; }
.speaker-c { color: #9B670D; font-weight: 600; }

.transcript-segment {
  font-family: 'Inter', sans-serif;
  padding: 0.4rem 0;
  border-bottom: 1px solid rgba(18, 118, 118, 0.15);
  line-height: 1.6;
  color: var(--retro-ink) !important;
}


.timestamp {
  font-family: 'Oswald', sans-serif;
  font-size: 0.8em;
  color: var(--retro-teal);
  margin-right: 0.5em;
}
</style>
"""

SPEAKER_COLORS = {
    0: ("#127676", "🟦"),
    1: ("#AD4117", "🟧"),
    2: ("#9B670D", "🟨"),
}

def inject_theme():
    css = RETRO_CSS.replace("{BG}", _bg_base64())
    st.markdown(css, unsafe_allow_html=True)

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

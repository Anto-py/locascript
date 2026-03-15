import os
import json
import queue
import subprocess
import sys
import time
import tempfile
import pathlib
import streamlit as st

LIVE_STATE_FILE = "/tmp/locascript_live.json"
PROJECT_ROOT = str(pathlib.Path(__file__).parent.parent)

from core.audio_capture import list_devices, AudioCaptureSession
from core.transcriber import MODELS
from core.translator import translate
from ui.theme import format_timestamp
from ui.file_tab import _export_section


TRANSLATE_LANGS = ["Anglais", "Français", "Espagnol", "Allemand", "Italien"]
LANG_CODE = {"Anglais": "en", "Français": "fr", "Espagnol": "es", "Allemand": "de", "Italien": "it"}
LANG_SRC_CODE = {"Automatique": None, "Français": "fr", "Anglais": "en",
                 "Espagnol": "es", "Allemand": "de", "Italien": "it"}


def _init_state():
    defaults = {
        "live_running":    False,
        "live_segments":   [],
        "live_start_time": None,
        "live_session":    None,
        "live_audio_queue": None,   # queue stockée dans session_state (survit au hot-reload)
        "live_last_error": None,
        "live_model_loaded": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render():
    _init_state()
    col_title, col_link = st.columns([3, 1])
    with col_title:
        st.header("Transcription en direct")
    with col_link:
        st.markdown(
            '<div style="text-align:right;padding-top:1rem">'
            '<a href="http://localhost:8502" target="_blank" '
            'style="color:#AD4117;font-weight:700;text-decoration:none">'
            '🖥️ Fenêtre d\'affichage</a></div>',
            unsafe_allow_html=True,
        )

    devices = list_devices()
    if not devices:
        st.error("Aucun périphérique audio détecté.")
        return

    device_names = [d["name"] for d in devices]
    device_label = st.selectbox("Source audio", device_names)
    selected_device = devices[device_names.index(device_label)]
    device_index = selected_device["index"]
    device_channels = selected_device["channels"]

    col1, col2 = st.columns(2)
    with col1:
        model_name = st.selectbox("Modèle Whisper", list(MODELS.keys()), index=2,
                                  key="live_model")
    with col2:
        chunk_seconds = st.slider("Durée des blocs (s)", 3, 30, 5, key="live_chunk")

    source_lang = st.selectbox(
        "Langue parlée",
        ["Automatique", "Français", "Anglais", "Espagnol", "Allemand", "Italien"],
        index=1,
        key="live_src_lang",
    )
    source_lang_code = LANG_SRC_CODE[source_lang]

    use_translation = st.toggle("Activer la traduction", value=False, key="live_trad")
    translate_to_lang = None
    if use_translation:
        tgt_label = st.selectbox("Langue cible", TRANSLATE_LANGS, key="live_trad_lang")
        translate_to_lang = LANG_CODE.get(tgt_label)

    # Format d'export
    st.markdown("**Format d'export**")
    col_f1, col_f2, col_f3 = st.columns(3)
    export_txt = col_f1.checkbox(".txt", value=True,  key="live_export_txt")
    export_md  = col_f2.checkbox(".md",  value=False, key="live_export_md")
    export_srt = col_f3.checkbox(".srt", value=False, key="live_export_srt")

    # Contrôles Start / Stop
    col_start, col_stop, col_status = st.columns([1, 1, 2])
    with col_start:
        start_disabled = st.session_state["live_running"]
        if st.button("▶ START", disabled=start_disabled, key="live_start"):
            _start(device_index, chunk_seconds, source_lang_code, device_channels)

    with col_stop:
        stop_disabled = not st.session_state["live_running"]
        if st.button("■ STOP", disabled=stop_disabled, key="live_stop"):
            _stop()

    with col_status:
        if st.session_state["live_running"]:
            elapsed = int(time.time() - (st.session_state["live_start_time"] or time.time()))
            st.markdown(
                f'<span style="color:#AD4117;font-weight:700">'
                f'● ENREGISTREMENT — {elapsed}s</span>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<span style="color:#127676">○ ARRÊTÉ</span>', unsafe_allow_html=True)

    # Afficher les erreurs éventuelles
    if st.session_state["live_last_error"]:
        st.error(f"Erreur transcription : {st.session_state['live_last_error']}")

    # Transcription dans le thread principal (MLX-safe)
    if st.session_state["live_running"]:
        audio_q = st.session_state.get("live_audio_queue")
        if audio_q and not audio_q.empty():
            with st.spinner("Transcription en cours…"):
                _process_audio_queue(audio_q, model_name, chunk_seconds, translate_to_lang, source_lang_code)
        # Toujours synchroniser la fenêtre d'affichage à chaque rerun
        _write_live_state(translate_to_lang is not None)

    # Zone de transcription live
    st.divider()
    transcript_area = st.empty()
    _render_live_transcript(transcript_area)

    # Export après arrêt (utilise les formats choisis avant le démarrage)
    if not st.session_state["live_running"] and st.session_state["live_segments"]:
        st.divider()
        _live_export_section(
            st.session_state["live_segments"],
            export_txt=st.session_state.get("live_export_txt", True),
            export_md=st.session_state.get("live_export_md", False),
            export_srt=st.session_state.get("live_export_srt", False),
        )

    # Auto-refresh pendant l'enregistrement
    if st.session_state["live_running"]:
        time.sleep(1)
        st.rerun()


def _process_audio_queue(audio_q, model_name, chunk_seconds, translate_to_lang, source_lang=None):
    """Transcrit les chunks audio en attente — s'exécute dans le thread principal."""
    start_time = st.session_state.get("live_start_time") or time.time()
    st.session_state["live_last_error"] = None

    while True:
        try:
            wav_bytes = audio_q.get_nowait()
        except queue.Empty:
            break

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name
        try:
            result = subprocess.run(
                [sys.executable, "-m", "core.transcribe_worker",
                 tmp_path, model_name, str(source_lang)],
                capture_output=True, text=True, cwd=PROJECT_ROOT,
            )
            if result.returncode != 0:
                st.session_state["live_last_error"] = result.stderr[-300:] or "Erreur subprocess"
                continue
            segs = json.loads(result.stdout)
            offset = time.time() - start_time
            for seg in segs:
                if translate_to_lang:
                    seg["translation"] = translate(seg["text"], translate_to_lang)
                seg["start"] += offset - chunk_seconds
                seg["end"]   += offset - chunk_seconds
                st.session_state["live_segments"].append(seg)
        except Exception as e:
            st.session_state["live_last_error"] = str(e)
        finally:
            os.unlink(tmp_path)


def _start(device_index, chunk_seconds, source_lang_code=None, channels=1):
    st.session_state["live_running"]    = True
    st.session_state["live_segments"]   = []
    st.session_state["live_start_time"] = time.time()
    st.session_state["live_last_error"] = None

    # Créer une nouvelle queue dans session_state (survit au hot-reload)
    audio_q: queue.Queue = queue.Queue()
    st.session_state["live_audio_queue"] = audio_q

    session = AudioCaptureSession(device_index, chunk_seconds=chunk_seconds, channels=channels)

    def on_chunk(wav_bytes: bytes):
        audio_q.put(wav_bytes)  # fermeture sur la queue locale, pas module-level

    session.start(on_chunk)
    st.session_state["live_session"] = session


def _write_live_state(has_translation: bool):
    """Écrit les groupes de segments dans un fichier JSON pour la fenêtre d'affichage."""
    segments = st.session_state.get("live_segments", [])
    groups = _group_segments(segments[-100:])

    serialized = []
    for group in groups:
        ts = max(0, group[0].get("start", 0))
        if has_translation:
            text = " ".join(s.get("translation", s.get("text", "")).strip() for s in group)
        else:
            text = " ".join(s.get("text", "").strip() for s in group)
        serialized.append({"start": ts, "text": text})

    data = {
        "running": st.session_state.get("live_running", False),
        "groups": serialized,
    }
    with open(LIVE_STATE_FILE, "w") as f:
        json.dump(data, f)


def _stop():
    st.session_state["live_running"] = False
    session = st.session_state.get("live_session")
    if session:
        session.stop()
        st.session_state["live_session"] = None


def _group_segments(segments, gap=1.0):
    """Regroupe les segments consécutifs séparés par moins de `gap` secondes."""
    if not segments:
        return []
    groups = [[segments[0]]]
    for seg in segments[1:]:
        if seg.get("start", 0) - groups[-1][-1].get("end", 0) > gap:
            groups.append([])
        groups[-1].append(seg)
    return groups


def _render_live_transcript(placeholder):
    segments = st.session_state.get("live_segments", [])
    if not segments:
        placeholder.info("En attente de l'audio…")
        return

    has_translation = any("translation" in s for s in segments)
    groups = _group_segments(segments[-100:])
    paragraphs = []

    for group in groups:
        if has_translation:
            text = " ".join(s.get("translation", s.get("text", "")).strip() for s in group)
        else:
            text = " ".join(s.get("text", "").strip() for s in group)
        if text.strip():
            paragraphs.append(text.strip())

    placeholder.markdown("\n\n".join(paragraphs))


def _live_export_section(segments, export_txt=True, export_md=False, export_srt=False):
    """Export live — sans timestamps, paragraphes séparés par les silences > 1s."""
    import datetime
    st.subheader("Export")

    has_translation = any("translation" in s for s in segments)
    groups = _group_segments(segments)
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    formats = [f for f, v in [(".txt", export_txt), (".md", export_md), (".srt", export_srt)] if v]
    st.caption(f"Formats sélectionnés : {', '.join(formats) if formats else 'aucun'}")

    def group_text(group):
        if has_translation:
            return " ".join(s.get("translation", s.get("text", "")).strip() for s in group)
        return " ".join(s.get("text", "").strip() for s in group)

    if export_txt:
        lines = [group_text(g) for g in groups if group_text(g).strip()]
        content = "\n\n".join(lines)
        st.download_button("Télécharger .txt", data=content,
                           file_name=f"live_{now}.txt", mime="text/plain")

    if export_md:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"# Transcription en direct — {date}\n\n---\n\n"
        lines = [group_text(g) for g in groups if group_text(g).strip()]
        content = header + "\n\n".join(lines)
        st.download_button("Télécharger .md", data=content,
                           file_name=f"live_{now}.md", mime="text/markdown")

    if export_srt:
        def srt_time(s):
            h, m = int(s // 3600), int((s % 3600) // 60)
            sec, ms = int(s % 60), int((s % 1) * 1000)
            return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
        srt_lines = []
        for i, group in enumerate(groups, 1):
            text = group_text(group).strip()
            if not text:
                continue
            start = srt_time(max(0, group[0].get("start", 0)))
            end   = srt_time(max(0, group[-1].get("end", 0)))
            srt_lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        content = "\n".join(srt_lines)
        st.download_button("Télécharger .srt", data=content,
                           file_name=f"live_{now}.srt", mime="text/plain")

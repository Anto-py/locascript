import os
import tempfile
import datetime
import streamlit as st

from core.pipeline import run
from core.transcriber import MODELS
from ui.theme import render_segment, format_timestamp


LANGUAGES = {
    "Détection automatique": None,
    "Français": "fr",
    "Anglais": "en",
    "Espagnol": "es",
    "Allemand": "de",
    "Italien": "it",
    "Portugais": "pt",
    "Japonais": "ja",
    "Chinois": "zh",
    "Arabe": "ar",
}

TRANSLATE_LANGS = ["Anglais", "Français", "Espagnol", "Allemand", "Italien"]


def render():
    st.header("Transcription de fichier")

    uploaded = st.file_uploader(
        "Déposer un fichier audio ou vidéo",
        type=["mp3", "mp4", "wav", "m4a", "ogg", "mov"],
    )

    col1, col2 = st.columns(2)
    with col1:
        lang_label = st.selectbox("Langue source", list(LANGUAGES.keys()))
        language = LANGUAGES[lang_label]
    with col2:
        model_name = st.selectbox("Modèle Whisper", list(MODELS.keys()), index=3)

    col3, col4 = st.columns(2)
    with col3:
        use_diarization = st.toggle("Identifier les locuteurs", value=True)
    with col4:
        use_translation = st.toggle("Activer la traduction", value=False)

    translate_to_en = False
    translate_to_lang = None
    if use_translation:
        target_label = st.selectbox("Langue cible", TRANSLATE_LANGS)
        if target_label == "Anglais":
            translate_to_en = True
        else:
            translate_to_lang = target_label

    if not uploaded:
        return

    if st.button("Lancer la transcription"):
        _process(
            uploaded, model_name, language,
            use_diarization, translate_to_en, translate_to_lang
        )


def _process(uploaded, model_name, language, use_diarization,
             translate_to_en, translate_to_lang):
    suffix = os.path.splitext(uploaded.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    status_text = st.empty()
    progress_bar = st.progress(0)

    def on_progress(step, pct):
        status_text.text(step)
        progress_bar.progress(pct)

    try:
        segments = run(
            tmp_path,
            model_name=model_name,
            language=language,
            use_diarization=use_diarization,
            translate_to_en=translate_to_en,
            translate_to_lang=translate_to_lang,
            progress_callback=on_progress,
        )
    finally:
        os.unlink(tmp_path)

    progress_bar.empty()
    status_text.empty()

    if not segments:
        st.warning("Aucun segment transcrit.")
        return

    st.session_state["file_segments"] = segments
    st.session_state["file_source_name"] = uploaded.name

    _display_results(segments, translate_to_en or bool(translate_to_lang))


def _display_results(segments: list, has_translation: bool):
    st.subheader("Transcription")

    if has_translation:
        col_orig, col_trad = st.columns(2)
        col_orig.markdown("**Original**")
        col_trad.markdown("**Traduction**")
        for seg in segments:
            with col_orig:
                render_segment(seg)
            with col_trad:
                trad_seg = {**seg, "text": seg.get("translation", ""), "speaker": ""}
                render_segment(trad_seg)
    else:
        for seg in segments:
            render_segment(seg)

    _export_section(segments)


def _export_section(segments: list):
    st.divider()
    st.subheader("Export")

    col1, col2, col3 = st.columns(3)
    export_txt = col1.checkbox(".txt", value=True)
    export_md  = col2.checkbox(".md",  value=False)
    export_srt = col3.checkbox(".srt", value=False)

    source_name = st.session_state.get("file_source_name", "transcription")
    base_name = os.path.splitext(source_name)[0]
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if export_txt:
        content = _to_txt(segments)
        st.download_button(
            "Télécharger .txt",
            data=content,
            file_name=f"{base_name}_{now}.txt",
            mime="text/plain",
        )

    if export_md:
        content = _to_md(segments, source_name)
        st.download_button(
            "Télécharger .md",
            data=content,
            file_name=f"{base_name}_{now}.md",
            mime="text/markdown",
        )

    if export_srt:
        content = _to_srt(segments)
        st.download_button(
            "Télécharger .srt",
            data=content,
            file_name=f"{base_name}_{now}.srt",
            mime="text/plain",
        )


def _to_txt(segments: list) -> str:
    lines = []
    for seg in segments:
        ts = format_timestamp(seg.get("start", 0))
        speaker = seg.get("speaker", "")
        text = seg.get("text", "").strip()
        prefix = f"[{ts}] {speaker.upper()} : " if speaker and speaker != "?" else f"[{ts}] "
        lines.append(prefix + text)
    return "\n".join(lines)


def _to_md(segments: list, source_name: str) -> str:
    from ui.theme import speaker_color
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    speakers = {s.get("speaker") for s in segments if s.get("speaker") and s.get("speaker") != "?"}
    header = (
        f"# Transcription — {source_name} — {now}\n"
        f"**Locuteurs :** {len(speakers)}\n\n---\n\n"
    )
    lines = [header]
    for seg in segments:
        ts = format_timestamp(seg.get("start", 0))
        speaker = seg.get("speaker", "")
        text = seg.get("text", "").strip()
        _, emoji = speaker_color(speaker) if speaker and speaker != "?" else ("", "")
        if speaker and speaker != "?":
            lines.append(f"**[{ts}] {emoji} {speaker.upper()}**\n{text}\n")
        else:
            lines.append(f"**[{ts}]**\n{text}\n")
    return "\n".join(lines)


def _to_srt(segments: list) -> str:
    def srt_time(s: float) -> str:
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = int(s % 60)
        ms = int((s % 1) * 1000)
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

    lines = []
    for i, seg in enumerate(segments, 1):
        start = srt_time(seg.get("start", 0))
        end   = srt_time(seg.get("end", 0))
        speaker = seg.get("speaker", "")
        text = seg.get("text", "").strip()
        prefix = f"[{speaker.upper()}] " if speaker and speaker != "?" else ""
        lines.append(f"{i}\n{start} --> {end}\n{prefix}{text}\n")
    return "\n".join(lines)

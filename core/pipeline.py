from core.transcriber import transcribe
from core.diarizer import diarize, load_diarizer
from core.translator import translate


def align(whisper_segments: list, diarization_segments: list) -> list:
    """Associe chaque segment Whisper à un locuteur pyannote."""
    result = []
    for seg in whisper_segments:
        mid = (seg["start"] + seg["end"]) / 2
        speaker = "?"
        for d in diarization_segments:
            if d["start"] <= mid <= d["end"]:
                speaker = d["speaker"]
                break
        result.append({**seg, "speaker": speaker})
    return result


def run(
    audio_path: str,
    model_name: str = "medium",
    language: str | None = None,
    use_diarization: bool = True,
    translate_to_en: bool = False,
    translate_to_lang: str | None = None,
    progress_callback=None,
) -> list[dict]:
    """
    Pipeline complet : transcription + diarisation + traduction.

    Retourne une liste de segments enrichis :
    [{"start", "end", "text", "speaker", "translation"?}, ...]

    progress_callback(step: str, pct: int) — appelé aux étapes clés.
    """
    def _progress(step, pct):
        if progress_callback:
            progress_callback(step, pct)

    # 1. Transcription
    _progress("Transcription en cours…", 10)
    segments = transcribe(audio_path, model_name=model_name, language=language,
                          translate_to_en=translate_to_en)
    _progress("Transcription terminée", 50)

    # 2. Diarisation
    if use_diarization:
        _progress("Diarisation en cours…", 55)
        try:
            pipeline = load_diarizer()
            diarization = diarize(audio_path, pipeline=pipeline)
            segments = align(segments, diarization)
        except EnvironmentError as e:
            # HF_TOKEN absent : on continue sans diarisation
            for seg in segments:
                seg.setdefault("speaker", "?")
        _progress("Diarisation terminée", 80)
    else:
        for seg in segments:
            seg["speaker"] = ""

    # 3. Traduction
    if translate_to_lang and not translate_to_en:
        _progress(f"Traduction vers {translate_to_lang}…", 85)
        for seg in segments:
            seg["translation"] = translate(seg["text"], translate_to_lang)
        _progress("Traduction terminée", 98)

    _progress("Terminé", 100)
    return segments

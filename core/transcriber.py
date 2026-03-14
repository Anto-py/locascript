import mlx_whisper

MODELS = {
    "tiny":     "mlx-community/whisper-tiny-mlx",
    "base":     "mlx-community/whisper-base-mlx",
    "small":    "mlx-community/whisper-small-mlx",
    "medium":   "mlx-community/whisper-medium-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
}

DEFAULT_MODEL = "medium"


def transcribe(
    audio_path: str,
    model_name: str = DEFAULT_MODEL,
    language: str | None = None,
    translate_to_en: bool = False,
) -> list[dict]:
    """
    Transcrit un fichier audio.

    Retourne une liste de segments :
    [{"start": float, "end": float, "text": str}, ...]
    """
    model_path = MODELS.get(model_name, MODELS[DEFAULT_MODEL])
    task = "translate" if translate_to_en else "transcribe"

    kwargs = dict(path_or_hf_repo=model_path, task=task, verbose=False)
    if language:
        kwargs["language"] = language

    result = mlx_whisper.transcribe(audio_path, **kwargs)

    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": seg["start"],
            "end":   seg["end"],
            "text":  seg["text"],
        })
    return segments

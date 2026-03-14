import os
from dotenv import load_dotenv

load_dotenv()

_pipeline = None


def load_diarizer():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    token = os.getenv("HF_TOKEN")
    if not token:
        raise EnvironmentError(
            "HF_TOKEN manquant dans .env — requis pour pyannote.audio. "
            "Créez un token sur https://huggingface.co et ajoutez-le dans .env"
        )

    from pyannote.audio import Pipeline
    _pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=token,
    )
    return _pipeline


def diarize(audio_path: str, pipeline=None) -> list[dict]:
    """
    Identifie les locuteurs dans un fichier audio.

    Retourne une liste de segments :
    [{"speaker": str, "start": float, "end": float}, ...]
    """
    if pipeline is None:
        pipeline = load_diarizer()

    diarization = pipeline(audio_path)
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start":   turn.start,
            "end":     turn.end,
        })
    return segments

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


def _to_16k_wav(audio_path: str) -> str:
    """Convertit l'audio en WAV 16kHz mono via torchaudio — requis par pyannote."""
    import tempfile
    import torchaudio

    waveform, sr = torchaudio.load(audio_path)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    torchaudio.save(tmp.name, waveform, 16000)
    return tmp.name


def diarize(audio_path: str, pipeline=None) -> list[dict]:
    """
    Identifie les locuteurs dans un fichier audio.

    Retourne une liste de segments :
    [{"speaker": str, "start": float, "end": float}, ...]
    """
    if pipeline is None:
        pipeline = load_diarizer()

    converted_path = _to_16k_wav(audio_path)
    try:
        result = pipeline(converted_path)
    finally:
        os.unlink(converted_path)

    # Compatibilité pyannote 3.x : DiarizeOutput.speaker_diarization ou Annotation directe
    if hasattr(result, "speaker_diarization"):
        annotation = result.speaker_diarization
    else:
        annotation = result

    segments = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start":   turn.start,
            "end":     turn.end,
        })
    return segments

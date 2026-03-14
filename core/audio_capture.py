import io
import threading
import pyaudio
import numpy as np
import wave

CHUNK = 1024
RATE = 16000
FORMAT = pyaudio.paInt16


def list_devices() -> list[dict]:
    """Retourne la liste des périphériques audio disponibles."""
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            devices.append({
                "index":    i,
                "name":     info["name"],
                "channels": int(info["maxInputChannels"]),
                "is_blackhole": "blackhole" in info["name"].lower(),
            })
    p.terminate()
    return devices


def get_default_device_index() -> int | None:
    devices = list_devices()
    if not devices:
        return None
    return devices[0]["index"]


class AudioCaptureSession:
    """
    Capture audio en continu depuis un périphérique PyAudio.
    Fonctionne dans un thread séparé pour ne pas bloquer Streamlit.
    """

    def __init__(self, device_index: int, chunk_seconds: int = 5, channels: int = 1):
        self.device_index = device_index
        self.chunk_seconds = chunk_seconds
        self.channels = channels
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._callback = None
        self._pa = None
        self._stream = None

    def start(self, on_chunk):
        """
        Démarre la capture.
        on_chunk(wav_bytes: bytes) est appelé toutes les `chunk_seconds` secondes.
        """
        self._callback = on_chunk
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _capture_loop(self):
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=FORMAT,
            channels=self.channels,
            rate=RATE,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=CHUNK,
        )

        frames_per_chunk = int(RATE / CHUNK * self.chunk_seconds)

        try:
            while not self._stop_event.is_set():
                frames = []
                for _ in range(frames_per_chunk):
                    if self._stop_event.is_set():
                        break
                    data = self._stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)

                if frames and self._callback:
                    wav_bytes = _frames_to_wav(frames, self.channels)
                    self._callback(wav_bytes)
        finally:
            self._stream.stop_stream()
            self._stream.close()
            self._pa.terminate()


def _frames_to_wav(frames: list[bytes], channels: int = 1) -> bytes:
    """Convertit des frames PCM brutes en bytes WAV 16kHz mono."""
    raw = b"".join(frames)

    # Si stéréo (ex: BlackHole 2ch), mixer en mono
    if channels == 2:
        samples = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2)
        raw = samples.mean(axis=1).astype(np.int16).tobytes()

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(raw)
    return buf.getvalue()

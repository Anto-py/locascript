"""
Worker de transcription isolé — lancé en sous-processus pour éviter
les conflits MLX/Metal avec Streamlit.

Usage : python -m core.transcribe_worker <audio_path> <model_name> [language]
Sortie : JSON sur stdout
"""
import sys
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

def main():
    audio_path = sys.argv[1]
    model_name = sys.argv[2]
    language   = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "None" else None

    from core.transcriber import transcribe
    segments = transcribe(audio_path, model_name=model_name, language=language)
    print(json.dumps(segments))

if __name__ == "__main__":
    main()

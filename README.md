# 🎙️ Locascript

Transcription audio locale, gratuite et privée — 100% sur votre machine, sans envoi de données.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red) ![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon-black) ![Licence](https://img.shields.io/badge/licence-MIT-green)

---

## Fonctionnalités

### 📁 Transcription de fichier
- Importe un fichier audio ou vidéo (`.mp3`, `.mp4`, `.wav`, `.m4a`, `.ogg`, `.mov`)
- Détection automatique ou forcée de la langue
- Identification des locuteurs (diarisation) — qui parle et quand
- Traduction vers une autre langue (Anglais, Espagnol, Allemand, Italien…)
- Choix du modèle Whisper selon la précision souhaitée (tiny → large-v3)
- Export en `.txt`, `.md` ou `.srt` (sous-titres)

### 🔴 Transcription en direct
- Capture la voix depuis le micro ou le son système (via BlackHole)
- Transcription par blocs (toutes les 3 à 30 secondes)
- Traduction en direct vers la langue cible
- **Fenêtre d'affichage dédiée** (`localhost:8502`) — plein écran, responsive, à placer à côté d'un PowerPoint ou d'une présentation
- Export de la session en fin d'enregistrement

---

## Prérequis système

> ⚠️ **macOS avec Apple Silicon (M1 / M2 / M3) uniquement.**
> Le moteur de transcription (mlx-whisper) est optimisé pour les puces Apple. Windows et Linux ne sont pas supportés dans cette version.

- macOS 13 Ventura ou supérieur
- Python 3.11+
- [Homebrew](https://brew.sh) (recommandé pour l'installation de Python)

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/Anto-py/locascript.git
cd locascript
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

---

### 4. Installer Ollama (traduction locale)

Ollama fait tourner des modèles de langage en local. Il est utilisé pour traduire vers des langues autres que l'anglais.

1. Télécharger et installer Ollama : [https://ollama.com/download](https://ollama.com/download)
2. Télécharger le modèle de traduction :

```bash
ollama pull mistral-nemo
```

3. Vérifier qu'Ollama tourne en arrière-plan avant de lancer l'app (il démarre automatiquement à l'installation).

---

### 5. Installer BlackHole (capture du son système)

BlackHole est un driver audio virtuel qui permet de capturer ce qui joue sur votre Mac (réunion Zoom, vidéo YouTube, etc.) pour le transcrire en direct.

> Si vous n'avez besoin que de transcrire votre microphone, cette étape est facultative.

1. Télécharger BlackHole 2ch : [https://existential.audio/blackhole/](https://existential.audio/blackhole/)
2. Suivre l'installeur (nécessite un redémarrage)
3. Après redémarrage, BlackHole 2ch apparaît dans la liste des sources audio de l'app

**Configuration recommandée pour capturer le son système :**
- Ouvrir **Configuration Audio Midi** (dans Applications > Utilitaires)
- Créer un **Périphérique agrégé** combinant votre sortie audio + BlackHole 2ch
- Sélectionner ce périphérique comme sortie dans les Réglages Son du Mac
- Dans Locascript, choisir BlackHole 2ch comme source

---

### 6. Configurer la diarisation (optionnel — identifier les locuteurs)

La diarisation permet de savoir qui parle à quel moment. Elle nécessite un compte Hugging Face gratuit.

1. Créer un compte : [https://huggingface.co](https://huggingface.co)
2. Accepter la licence du modèle : [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. Générer un token d'accès (lecture) : [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Créer un fichier `.env` à la racine du projet :

```bash
echo "HF_TOKEN=hf_votre_token_ici" > .env
```

> Sans token, l'app fonctionne normalement — la diarisation est simplement désactivée.

---

## Lancement

```bash
source .venv/bin/activate
streamlit run app.py
```

L'app s'ouvre sur [http://localhost:8501](http://localhost:8501).

La **fenêtre d'affichage** (transcription plein écran pour présentations) est disponible sur [http://localhost:8502](http://localhost:8502) — elle se lance automatiquement.

---

## Modèles Whisper disponibles

| Modèle | Taille | Vitesse | Qualité |
|--------|--------|---------|---------|
| tiny | 75 MB | ⚡⚡⚡⚡ | ★☆☆☆ |
| base | 145 MB | ⚡⚡⚡ | ★★☆☆ |
| small | 480 MB | ⚡⚡ | ★★★☆ |
| medium | 1.5 GB | ⚡ | ★★★★ — recommandé |
| large-v3 | 3 GB | 🐌 | ★★★★★ |

Les modèles sont téléchargés automatiquement au premier lancement. Prévoir de la place disque et quelques minutes la première fois.

---

## Stack technique

- **[mlx-whisper](https://github.com/ml-explore/mlx-examples)** — transcription optimisée Apple Silicon
- **[pyannote.audio](https://github.com/pyannote/pyannote-audio)** — diarisation (identification des locuteurs)
- **[Ollama](https://ollama.com) + mistral-nemo** — traduction locale
- **[Streamlit](https://streamlit.io)** — interface web locale
- **[BlackHole](https://existential.audio/blackhole/)** — capture audio système
- **[PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)** — capture microphone en temps réel

---

## Confidentialité

Aucune donnée ne quitte votre machine. Tout tourne en local :
- Transcription : mlx-whisper en local
- Traduction : Ollama en local
- Diarisation : pyannote en local

Seul le téléchargement initial des modèles nécessite une connexion internet.

---

## Licence

MIT — libre d'utilisation, de modification et de distribution.

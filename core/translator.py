import ollama


def translate(text: str, target_lang: str) -> str:
    """
    Traduit un texte vers target_lang via Ollama (mistral-nemo local).
    Retourne uniquement la traduction.
    """
    if not text.strip():
        return ""

    response = ollama.chat(
        model="mistral-nemo",
        messages=[{
            "role": "user",
            "content": (
                f"Traduis en {target_lang}. "
                f"Réponds uniquement avec la traduction, sans commentaire :\n\n{text}"
            ),
        }],
    )
    return response["message"]["content"].strip()

from korean_romanizer.romanizer import Romanizer

def korean_to_romanization(korean_text: str) -> str:
    """
    Convert Korean text to romanization using Revised Romanization of Korean
    """
    try:
        r = Romanizer(korean_text)
        return r.romanize()
    except Exception as e:
        print(f"Warning: Romanization failed for '{korean_text}': {e}")
        return korean_text.lower()  # Fallback
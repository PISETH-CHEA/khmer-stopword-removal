import unicodedata

def normalize_text(text):
    normalized = unicodedata.normalize('NFKC', text)
    return normalized.strip()

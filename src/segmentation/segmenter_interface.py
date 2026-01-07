from khmernltk import word_tokenize


class KhmerSegmenter:
    def __init__(self, model="khmer-nltk"):
        self.model = model

    def segment(self, text):
        try:
            tokens = word_tokenize(text)
            return [token.strip() for token in tokens if token.strip()]
        except Exception as e:
            print(f"Segmentation error: {e}")
            return []

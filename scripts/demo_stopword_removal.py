import sys
import os
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.segmentation.segmenter_interface import KhmerSegmenter
from src.preprocessing.unicode_normalizer import normalize_text
import yaml


class KhmerStopwordRemover:
    def __init__(self, stopwords_path="data/stopwords/final_stopword_list.txt"):
        self.segmenter = KhmerSegmenter()
        self.stopwords = self.load_stopwords(stopwords_path)

    def load_stopwords(self, filepath):
        stopwords = set()
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    stopwords.add(line.strip())
        return stopwords

    def remove_stopwords(self, text):
        normalized = normalize_text(text)
        tokens = self.segmenter.segment(normalized)
        filtered = [token for token in tokens if token not in self.stopwords]
        return filtered

    def get_stats(self, original_tokens, filtered_tokens):
        removed = len(original_tokens) - len(filtered_tokens)
        ratio = removed / len(original_tokens) * 100
        return removed, ratio
    
    def Frequency(self, tokens):
        # Count the frequency of each token
        token_counts = Counter(tokens)
        return dict(token_counts)

    def linguistic_features(self, tokens):
        features = {
            'total_tokens': len(tokens),
            'unique_tokens': len(set(tokens)),
        }
        return features

    def segmented_text(self, text):
        normalized = normalize_text(text)
        return self.segmenter.segment(normalized)


def main():
    # Sample Khmer texts for demonstration
    sample_texts = [
        "កម្ពុជាជាប្រទេសដែលមានប្រជាជនជាងដប់ប្រាំមួយលាននាក់នៅឆ្នាំ២០២៥",
        "ខ្ញុំចូលចិត្តញ៉ាំបាយនិងផ្លែឈើដែលមានរសជាតិផ្អែម",
        "ការអប់រំគឺជាកូនសោរសម្រាប់អនាគតដ៏ភ្លឺស្វាង",
        "ពួកយើងទាំងអស់គ្នាត្រូវការសុខភាពល្អដើម្បីរស់នៅបានសុខសាន្ត",
    ]

    print("=== KHMER STOPWORD REMOVAL DEMO ===\n")

    remover = KhmerStopwordRemover()
    print(f"Loaded {len(remover.stopwords)} stopwords\n")

    for i, text in enumerate(sample_texts, 1):
        print(f"--- Sample {i} ---")
        print(f"Original: {text}")

        tokens = remover.segmenter.segment(normalize_text(text))
        filtered = remover.remove_stopwords(text)
        removed, ratio = remover.get_stats(tokens, filtered)
        frequency = remover.Frequency(tokens)
        linguistic_ = remover.linguistic_features(tokens)
        segmented_ = remover.segmented_text(text)
        
        print(f"Tokens before: {len(tokens)}")
        print(f"Tokens after: {len(filtered)}")
        print(f"frequency   : {frequency}")
        print(f"linguistic   : {linguistic_}")
        print(f"Segmented Text: {' | '.join(segmented_)}")
        print(f"Removed: {removed} ({ratio:.1f}%)")
        print(
            f"Result: {' | '.join(filtered[:10])}{'...' if len(filtered) > 10 else ''}\n"
        )


if __name__ == "__main__":
    main()

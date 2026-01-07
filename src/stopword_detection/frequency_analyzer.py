import os
import glob
from collections import Counter, defaultdict
import yaml


class FrequencyAnalyzer:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.threshold = self.config["stopword_detection"]["frequency_threshold"]
        self.min_docs = self.config["stopword_detection"]["min_doc_frequency"]

    def analyze_corpus(self, segmented_dir):
        doc_count = 0
        word_doc_freq = defaultdict(int)
        total_word_counts = Counter()

        for filepath in glob.glob(os.path.join(segmented_dir, "*_segmented.txt")):
            doc_count += 1
            with open(filepath, "r", encoding="utf-8") as f:
                tokens = f.read().split()
                unique_tokens = set(tokens)

                for token in unique_tokens:
                    word_doc_freq[token] += 1

                total_word_counts.update(tokens)

        candidate_stopwords = []
        for word, doc_freq in word_doc_freq.items():
            doc_frequency_ratio = doc_freq / doc_count
            if doc_frequency_ratio >= self.threshold and doc_freq >= self.min_docs:
                candidate_stopwords.append(
                    {
                        "word": word,
                        "doc_frequency": doc_freq,
                        "doc_frequency_ratio": doc_frequency_ratio,
                        "total_count": total_word_counts[word],
                    }
                )

        return sorted(
            candidate_stopwords, key=lambda x: x["doc_frequency_ratio"], reverse=True
        )

    def save_candidates(self, candidates, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            for item in candidates:
                f.write(
                    f"{item['word']}\t{item['doc_frequency_ratio']:.3f}\t{item['total_count']}\n"
                )

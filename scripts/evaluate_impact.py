import sys
import os
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class ImpactEvaluator:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.segmented_dir = self.config["data_paths"]["segmented_dir"]
        self.stopwords_dir = self.config["data_paths"]["stopwords_dir"]

    def load_stopword_candidates(self):
        freq_path = os.path.join(self.stopwords_dir, "frequency_candidates.txt")
        ling_path = os.path.join(self.stopwords_dir, "linguistic_candidates.txt")

        stopwords = set()

        if os.path.exists(freq_path):
            with open(freq_path, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.split("\t")[0].strip()
                    stopwords.add(word)

        if os.path.exists(ling_path):
            with open(ling_path, "r", encoding="utf-8") as f:
                for line in f:
                    stopwords.add(line.strip())

        return list(stopwords)

    def create_final_stopword_list(self):
        stopwords = self.load_stopword_candidates()
        final_path = os.path.join(self.stopwords_dir, "final_stopword_list.txt")

        with open(final_path, "w", encoding="utf-8") as f:
            for word in sorted(stopwords):
                f.write(f"{word}\n")

        print(f"Final stopword list created with {len(stopwords)} words")
        return stopwords

    def load_documents(self):
        documents = {}

        for filepath in glob.glob(os.path.join(self.segmented_dir, "*_segmented.txt")):
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                documents[filename] = f.read()

        return documents

    def evaluate_tfidf_impact(self, stopwords):
        documents = self.load_documents()

        if len(documents) < 2:
            print("Need at least 2 documents for evaluation")
            return None

        doc_texts = list(documents.values())
        doc_names = list(documents.keys())

        # Without stopwords
        vectorizer_without = TfidfVectorizer()
        tfidf_without = vectorizer_without.fit_transform(doc_texts)
        vocab_without = vectorizer_without.get_feature_names_out()

        # With stopwords
        vectorizer_with = TfidfVectorizer(stop_words=stopwords)
        tfidf_with = vectorizer_with.fit_transform(doc_texts)
        vocab_with = vectorizer_with.get_feature_names_out()

        print("\n=== TF-IDF IMPACT ANALYSIS ===")
        print(f"Without stopwords: {len(vocab_without)} terms")
        print(f"With stopwords: {len(vocab_with)} terms")
        print(
            f"Vocabulary reduction: {len(vocab_without) - len(vocab_with)} terms ({100*(1-len(vocab_with)/len(vocab_without)):.1f}%)"
        )

        # Show top terms per document
        for i, doc_name in enumerate(doc_names):
            print(f"\n--- {doc_name} ---")

            # Without stopwords
            scores_without = tfidf_without[i].toarray()[0]
            top_idx_without = np.argsort(scores_without)[-5:][::-1]
            top_terms_without = [vocab_without[idx] for idx in top_idx_without]
            print(f"Top terms (without): {', '.join(top_terms_without)}")

            # With stopwords
            scores_with = tfidf_with[i].toarray()[0]
            top_idx_with = np.argsort(scores_with)[-5:][::-1]
            top_terms_with = [vocab_with[idx] for idx in top_idx_with]
            print(f"Top terms (with): {', '.join(top_terms_with)}")

        # Calculate similarity matrix
        sim_without = cosine_similarity(tfidf_without)
        sim_with = cosine_similarity(tfidf_with)

        print("\n=== DOCUMENT SIMILARITY ===")
        print("Similarity without stopwords:")
        print(np.round(sim_without, 3))
        print("\nSimilarity with stopwords:")
        print(np.round(sim_with, 3))

        return {
            "vocab_reduction": len(vocab_without) - len(vocab_with),
            "vocab_reduction_percent": 100 * (1 - len(vocab_with) / len(vocab_without)),
            "avg_similarity_without": np.mean(sim_without),
            "avg_similarity_with": np.mean(sim_with),
        }


def main():
    evaluator = ImpactEvaluator()
    stopwords = evaluator.create_final_stopword_list()
    metrics = evaluator.evaluate_tfidf_impact(stopwords)

    if metrics:
        print("\n=== IMPACT SUMMARY ===")
        print(
            f"Vocabulary reduction: {metrics['vocab_reduction']} terms ({metrics['vocab_reduction_percent']:.1f}%)"
        )
        print(f"Avg similarity without: {metrics['avg_similarity_without']:.3f}")
        print(f"Avg similarity with: {metrics['avg_similarity_with']:.3f}")


if __name__ == "__main__":
    main()

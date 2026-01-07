import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.stopword_detection.frequency_analyzer import FrequencyAnalyzer
from src.stopword_detection.linguistic_rules import LinguisticRules
import yaml


def main():
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    segmented_dir = config["data_paths"]["segmented_dir"]
    stopwords_dir = config["data_paths"]["stopwords_dir"]

    print("Running frequency analysis...")
    freq_analyzer = FrequencyAnalyzer()
    freq_candidates = freq_analyzer.analyze_corpus(segmented_dir)

    freq_output = os.path.join(stopwords_dir, "frequency_candidates.txt")
    freq_analyzer.save_candidates(freq_candidates, freq_output)
    print(f"Found {len(freq_candidates)} frequency-based candidates")

    print("Building vocabulary for linguistic analysis...")
    ling_rules = LinguisticRules()
    vocabulary = ling_rules.build_vocabulary(segmented_dir)
    print(f"Total vocabulary size: {len(vocabulary)}")

    print("Applying linguistic rules...")
    ling_candidates = ling_rules.identify_linguistic_stopwords(vocabulary)

    ling_output = os.path.join(stopwords_dir, "linguistic_candidates.txt")
    ling_rules.save_candidates(ling_candidates, ling_output)
    print(f"Found {len(ling_candidates)} linguistic candidates")

    print("Stop-word extraction complete!")


if __name__ == "__main__":
    main()

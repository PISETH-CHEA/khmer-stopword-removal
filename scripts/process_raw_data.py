import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing.text_loader import load_corpus, save_segmented
from src.segmentation.segmenter_interface import KhmerSegmenter
from src.preprocessing.unicode_normalizer import normalize_text
import yaml


def main():
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    raw_dir = config["data_paths"]["raw_dir"]
    segmented_dir = config["data_paths"]["segmented_dir"]

    print("Loading raw corpus...")
    corpus = load_corpus(raw_dir)

    print("Initializing segmenter...")
    segmenter = KhmerSegmenter()

    print("Processing documents...")
    for doc_id, text in corpus.items():
        normalized = normalize_text(text)
        segmented = segmenter.segment(normalized)
        save_segmented(doc_id, segmented, segmented_dir)
        print(f"Processed: {doc_id} ({len(segmented)} tokens)")

    print(f"Segmentation complete. Files saved to {segmented_dir}")


if __name__ == "__main__":
    main()

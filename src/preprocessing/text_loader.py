import os
import glob

def load_corpus(raw_dir):
    corpus = {}
    for filepath in glob.glob(os.path.join(raw_dir, "*.txt")):
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            corpus[filename] = f.read()
    return corpus

def save_segmented(doc_id, segmented_text, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{doc_id}_segmented.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(' '.join(segmented_text))

import os
import glob


class LinguisticRules:
    def __init__(self):
        self.function_words = {
            "ខ្ញុំ",
            "អ្នក",
            "គាត់",
            "យើង",
            "ពួកគេ",
            "វា",
            "នៅ",
            "ក្នុង",
            "លើ",
            "ក្រោម",
            "ខាង",
            "ជិត",
            "ឆ្ងាយ",
            "និង",
            "ឬ",
            "ប៉ុន្តែ",
            "ដូច្នេះ",
            "ព្រោះ",
            "ទោះបី",
            "ជា",
            "ដែល",
            "អំពី",
            "ដោយ",
            "សម្រាប់",
            "ពី",
            "នេះ",
            "នោះ",
            "ទាំង",
            "គ្រប់",
            "អស់",
            "មួយ",
            "គឺ",
            "មាន",
            "ធ្វើ",
            "បាន",
            "ជាមួយ",
            "អ្វី",
            "ណា",
            "ដូចម្ដេច",
            "ហេតុអ្វី",
            "នៅឯណា",
        }

    def build_vocabulary(self, segmented_dir):
        vocabulary = set()
        for filepath in glob.glob(os.path.join(segmented_dir, "*_segmented.txt")):
            with open(filepath, "r", encoding="utf-8") as f:
                tokens = f.read().split()
                vocabulary.update(tokens)
        return vocabulary

    def identify_linguistic_stopwords(self, vocabulary):
        return [word for word in vocabulary if word in self.function_words]

    def save_candidates(self, candidates, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            for word in sorted(candidates):
                f.write(f"{word}\n")

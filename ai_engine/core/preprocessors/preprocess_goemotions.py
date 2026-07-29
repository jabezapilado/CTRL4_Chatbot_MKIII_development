"""
GoEmotions Dataset Preprocessor

Converts the original GoEmotions dataset into the
CTRL4 standardized dataset format.

Author: CTRL4 Chatbot MK2
"""

import csv

from datasets import Dataset, DatasetDict

from ai_engine.core.preprocessors.base_preprocessor import BasePreprocessor


class GoEmotionsPreprocessor(BasePreprocessor):

    def __init__(self):
        super().__init__("goemotions")

        self.external_dir = (
            self.data_dir
            / "external"
            / "goemotions"
        )

        self.label_map = self.load_labels()

    def load_labels(self):

        labels = {}

        emotion_file = self.external_dir / "emotions.txt"

        with open(emotion_file, "r", encoding="utf-8") as file:

            for index, emotion in enumerate(file):

                labels[str(index)] = emotion.strip()

        return labels

    def process_split(self, filename):

        path = self.external_dir / filename

        rows = []

        with open(path, "r", encoding="utf-8") as file:

            reader = csv.reader(file, delimiter="\t")

            for index, row in enumerate(reader):

                if len(row) < 2:
                    continue

                text = row[0]

                label_ids = row[1].split(",")

                original = self.label_map.get(
                    label_ids[0],
                    "neutral"
                )

                emotion = self.map_emotion(original)

                record = self.build_record(
                    record_id=self.generate_id("GOE", index + 1),
                    text=text,
                    original_emotion=original,
                    emotion=emotion,
                    source="GoEmotions"
                )

                if self.validate_record(record):
                    rows.append(record)

        return Dataset.from_list(rows)

    def run(self):

        train = self.process_split("train.tsv")
        validation = self.process_split("dev.tsv")
        test = self.process_split("test.tsv")

        dataset = DatasetDict({
            "train": train,
            "validation": validation,
            "test": test
        })

        self.save_dataset(dataset)

        self.print_summary(
            len(train),
            len(validation),
            len(test)
        )


if __name__ == "__main__":

    GoEmotionsPreprocessor().run()
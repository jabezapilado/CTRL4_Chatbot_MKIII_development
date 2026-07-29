"""
DAIR-AI Emotion Dataset Preprocessor

Converts the DAIR-AI Emotion dataset into the
CTRL4 standardized dataset format.

Author: CTRL4 Chatbot MK2
"""

from datasets import Dataset, DatasetDict, load_from_disk

from ai_engine.core.preprocessors.base_preprocessor import BasePreprocessor


LABEL_MAP = {
    0: "sadness",
    1: "joy",
    2: "love",
    3: "anger",
    4: "fear",
    5: "surprise",
}


class DAIRPreprocessor(BasePreprocessor):

    def __init__(self):

        super().__init__("dair_ai")

        self.external_dir = (
            self.data_dir
            / "external"
            / "dair_ai_emotion"
        )

    def process_split(self, dataset_split, prefix):

        rows = []

        for index, row in enumerate(dataset_split):

            text = row["text"]

            original_emotion = LABEL_MAP[row["label"]]

            emotion = self.map_emotion(
                original_emotion
            )

            record = self.build_record(

                record_id=self.generate_id(
                    prefix,
                    index + 1
                ),

                text=text,

                original_emotion=original_emotion,

                emotion=emotion,

                source="DAIR-AI"

            )

            if self.validate_record(record):

                rows.append(record)

        return Dataset.from_list(rows)

    def run(self):

        dataset = load_from_disk(
            self.external_dir
        )

        train = self.process_split(
            dataset["train"],
            "DAIR_TR"
        )

        validation = self.process_split(
            dataset["validation"],
            "DAIR_VAL"
        )

        test = self.process_split(
            dataset["test"],
            "DAIR_TE"
        )

        final_dataset = DatasetDict({

            "train": train,

            "validation": validation,

            "test": test

        })

        self.save_dataset(
            final_dataset
        )

        self.print_summary(

            len(train),

            len(validation),

            len(test)

        )


if __name__ == "__main__":

    DAIRPreprocessor().run()
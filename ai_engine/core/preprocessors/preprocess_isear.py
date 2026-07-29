"""
ISEAR Dataset Preprocessor

Converts the ISEAR dataset into the
CTRL4 standardized dataset format.

Author: CTRL4 Chatbot MK2
"""

import pandas as pd

from datasets import Dataset, DatasetDict

from ai_engine.core.preprocessors.base_preprocessor import BasePreprocessor


class ISEARPreprocessor(BasePreprocessor):

    def __init__(self):
        super().__init__("isear")

        self.external_dir = (
            self.data_dir
            / "external"
            / "isear"
        )

    def process_dataset(self):

        csv_file = self.external_dir / "ISEAR_eng_dataset.csv"

        df = pd.read_csv(csv_file)

        rows = []

        for index, row in df.iterrows():

            text = str(row["content"]).strip()

            original_emotion = str(
                row["sentiment"]
            ).strip().lower()

            emotion = self.map_emotion(
                original_emotion
            )

            record = self.build_record(

                record_id=self.generate_id(
                    "ISE",
                    index + 1
                ),

                text=text,

                original_emotion=original_emotion,

                emotion=emotion,

                source="ISEAR"

            )

            if self.validate_record(record):

                rows.append(record)

        return Dataset.from_list(rows)

    def run(self):

        dataset = self.process_dataset()

        split_1 = dataset.train_test_split(
            test_size=0.20,
            seed=42
        )

        split_2 = split_1["test"].train_test_split(
            test_size=0.50,
            seed=42
        )

        final_dataset = DatasetDict({

            "train": split_1["train"],

            "validation": split_2["train"],

            "test": split_2["test"]

        })

        self.save_dataset(
            final_dataset
        )

        self.print_summary(

            len(final_dataset["train"]),

            len(final_dataset["validation"]),

            len(final_dataset["test"])

        )


if __name__ == "__main__":

    ISEARPreprocessor().run()
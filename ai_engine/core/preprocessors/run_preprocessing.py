"""
CTRL4 Dataset Preprocessing Pipeline

Runs all dataset preprocessors.

Author: CTRL4 Chatbot MK2
"""
from ai_engine.core.preprocessors.preprocess_dair import (
    DAIRPreprocessor,
)

from ai_engine.core.preprocessors.preprocess_goemotions import (
    GoEmotionsPreprocessor,
)

from ai_engine.core.preprocessors.preprocess_isear import (
    ISEARPreprocessor,
)



def main():

    preprocessors = [

        GoEmotionsPreprocessor(),

        ISEARPreprocessor(),
        
        DAIRPreprocessor(),

    ]

    print()
    print("=" * 60)
    print("CTRL4 CHATBOT MK2")
    print("DATA PREPROCESSING PIPELINE")
    print("=" * 60)

    successful = 0

    failed = 0

    for processor in preprocessors:

        print()

        print(f"Running: {processor.dataset_name}")

        try:

            processor.run()

            successful += 1

        except Exception as error:

            failed += 1

            print()

            print(f"ERROR while processing {processor.dataset_name}")

            print(error)

    print()

    print("=" * 60)
    print("PIPELINE FINISHED")
    print("=" * 60)

    print(f"Successful : {successful}")

    print(f"Failed     : {failed}")

    print("=" * 60)


if __name__ == "__main__":

    main()
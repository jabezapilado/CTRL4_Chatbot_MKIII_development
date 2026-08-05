# Emotion Label Lineage Report

Last updated: 2026-08-01

## Scope

This report traces exactly where emotion labels originate and how they move through:

1. Preprocessing
2. Training
3. Evaluation
4. Inference

It also identifies which label files are authoritative versus legacy/not used in the active model path.

## Canonical Label Source of Truth

Primary canonical classes are defined in:

- ai_engine/configs/label_encoder.json

Current canonical mapping:

- Positive -> 0
- Neutral -> 1
- Anger -> 2
- Sadness -> 3
- Fear -> 4

Code checkpoints:

- ai_engine/configs/label_encoder.json:1
- ai_engine/core/preprocessors/base_preprocessor.py:56
- ai_engine/core/training/dataset.py:33
- backend/server/services/emotion_service.py:29

Model output size is fixed to 5 classes:

- ai_engine/configs/model_config.json:4
- ai_engine/core/models/emotion_classifier.py:23

## Dataset Label Origins

### 1) GoEmotions

Origin path:

- Source labels loaded from emotions.txt via indexed IDs.
- During row processing, the first label ID is selected for multi-label rows.

Code checkpoints:

- ai_engine/core/preprocessors/preprocess_goemotions.py:30
- ai_engine/core/preprocessors/preprocess_goemotions.py:34
- ai_engine/core/preprocessors/preprocess_goemotions.py:61
- ai_engine/core/preprocessors/preprocess_goemotions.py:67

Flow:

1. label_ids[0] -> original emotion text
2. original emotion text -> map_emotion(...)
3. canonical emotion -> record

### 2) ISEAR

Origin path:

- Source label read from CSV sentiment column.

Code checkpoints:

- ai_engine/core/preprocessors/preprocess_isear.py:41
- ai_engine/core/preprocessors/preprocess_isear.py:44

Flow:

1. row[sentiment] -> original_emotion
2. original_emotion -> map_emotion(...)
3. canonical emotion -> record

### 3) DAIR-AI Emotion

Origin path:

- Integer label is converted by LABEL_MAP.

Code checkpoints:

- ai_engine/core/preprocessors/preprocess_dair.py:15
- ai_engine/core/preprocessors/preprocess_dair.py:45
- ai_engine/core/preprocessors/preprocess_dair.py:47

DAIR LABEL_MAP:

- 0 -> sadness
- 1 -> joy
- 2 -> love
- 3 -> anger
- 4 -> fear
- 5 -> surprise

Flow:

1. numeric label -> LABEL_MAP original_emotion
2. original_emotion -> map_emotion(...)
3. canonical emotion -> record

## Preprocessing Transformation Layer

All source datasets pass through BasePreprocessor.

Code checkpoints:

- ai_engine/core/preprocessors/base_preprocessor.py:48
- ai_engine/core/preprocessors/base_preprocessor.py:52
- ai_engine/core/preprocessors/base_preprocessor.py:56
- ai_engine/core/preprocessors/base_preprocessor.py:102
- ai_engine/core/preprocessors/base_preprocessor.py:110
- ai_engine/core/preprocessors/base_preprocessor.py:143
- ai_engine/core/preprocessors/base_preprocessor.py:155
- ai_engine/core/preprocessors/base_preprocessor.py:157
- ai_engine/core/preprocessors/base_preprocessor.py:184

### Full source-to-canonical emotion mapping

Mapping file:

- ai_engine/configs/emotion_mapping.json

Positive group:

- admiration, amusement, approval, caring, desire, excitement, gratitude, joy, love, optimism, pride, relief -> Positive

Neutral group:

- curiosity, realization, surprise, confusion, neutral -> Neutral

Anger group:

- anger, annoyance, disapproval, disgust, frustration -> Anger

Fear group:

- fear, nervousness, anxiety, worry, worried, panic, stress -> Fear

Sadness group:

- sadness, disappointment, embarrassment, remorse, hopelessness, grief, burnout, loneliness -> Sadness

Code checkpoint:

- ai_engine/configs/emotion_mapping.json:1

### Sentiment and negativity mapping

Applied in preprocessing via map_sentiment(emotion).

Code checkpoints:

- ai_engine/core/preprocessors/base_preprocessor.py:110
- ai_engine/configs/sentiment_mapping.json:1

Record schema fields produced during preprocessing:

- id
- text
- original_emotion
- emotion
- sentiment
- is_negative
- source

Schema definition:

- ai_engine/core/schemas/emotion_record.py:11
- ai_engine/core/schemas/emotion_record.py:17

### Validation gate before save

Preprocessor record validation enforces canonical emotion membership using label_encoder keys.

Code checkpoints:

- ai_engine/core/preprocessors/base_preprocessor.py:61
- ai_engine/core/preprocessors/base_preprocessor.py:184

## Merge Layer

Processed splits are concatenated and cleaned before training.

Code checkpoints:

- ai_engine/core/preprocessors/merge_datasets.py:81
- ai_engine/core/preprocessors/merge_datasets.py:83
- ai_engine/core/preprocessors/merge_datasets.py:85
- ai_engine/core/preprocessors/merge_datasets.py:90
- ai_engine/core/preprocessors/merge_datasets.py:111
- ai_engine/core/preprocessors/merge_datasets.py:128
- ai_engine/core/preprocessors/merge_datasets.py:199
- ai_engine/core/preprocessors/merge_datasets.py:201
- ai_engine/core/preprocessors/merge_datasets.py:208

Flow behavior:

1. Concatenate train/validation/test across datasets.
2. Deduplicate normalized text within each split.
3. Remove validation rows whose normalized text already exists in train.
4. Remove test rows whose normalized text exists in train or validation.
5. Shuffle and save merged_emotion_dataset.

## Training Label Flow

Training loads merged_emotion_dataset, filters to allowed canonical labels, encodes numeric labels, and trains 5-class DistilBERT.

Code checkpoints:

- ai_engine/core/training/dataset.py:27
- ai_engine/core/training/dataset.py:43
- ai_engine/core/training/dataset.py:49
- ai_engine/core/training/dataset.py:51
- ai_engine/core/training/dataset.py:79
- ai_engine/core/training/dataset.py:86
- ai_engine/core/models/emotion_classifier.py:23
- ai_engine/configs/model_config.json:4

Numeric label encoding operation:

1. example[emotion] (string)
2. label_encoder[emotion]
3. example[labels] (int 0..4)

Training metrics compute over numeric IDs:

- ai_engine/core/training/metrics.py:19
- ai_engine/core/training/metrics.py:22

Trainer config uses eval_f1 for best model selection:

- ai_engine/core/training/trainer.py:60

## Evaluation Label Flow

Evaluation imports label_encoder from training dataset module and derives class-name ordering from encoder indices.

Code checkpoints:

- ai_engine/core/training/evaluate_model.py:10
- ai_engine/core/training/evaluate_model.py:31
- ai_engine/core/training/evaluate_model.py:33

Flow:

1. Test dataset provides label_ids (numeric 0..4).
2. Predictions are argmax(logits) numeric IDs.
3. Metrics are computed on numeric IDs.
4. Confusion matrix and classification report use CLASS_NAMES from sorted(label_encoder by index).

Code checkpoints:

- ai_engine/core/training/evaluate_model.py:60
- ai_engine/core/training/evaluate_model.py:135
- ai_engine/core/training/evaluate_model.py:186
- ai_engine/core/training/evaluate_model.py:190

## Inference Label Flow

Runtime inference loads model logits, converts to class index, maps index to canonical class via label_encoder inversion, then derives sentiment and is_negative.

Code checkpoints:

- backend/server/services/emotion_service.py:27
- backend/server/services/emotion_service.py:35
- backend/server/services/emotion_service.py:148
- backend/server/services/emotion_service.py:154
- backend/server/services/emotion_service.py:161
- backend/server/services/emotion_service.py:177

Flow:

1. label_encoder.json is inverted to LABELS dict[int, str].
2. prediction index = argmax(probabilities).
3. emotion = LABELS[prediction].
4. If emotion is not Positive, normalize_emotion(text, emotion) may remap:
   - stress or anxiety keywords -> Fear
   - loneliness keywords -> Sadness
5. sentiment/is_negative are assigned from runtime emotion sets:
   - Anger/Sadness/Fear -> Negative/True
   - Positive -> Positive/False
   - Neutral -> Neutral/False
6. Response object is EmotionPrediction(emotion, sentiment, confidence, is_negative).

## Validator Cross-Check

Validator ensures saved datasets comply with canonical labels and sentiment set.

Code checkpoints:

- ai_engine/core/utilities/validate_dataset.py:215
- ai_engine/core/utilities/validate_dataset.py:218
- ai_engine/core/utilities/validate_dataset.py:219
- ai_engine/core/utilities/validate_dataset.py:95
- ai_engine/core/utilities/validate_dataset.py:99

## Authoritative vs Legacy Label Files

Active path (used in preprocessing/training/eval/inference):

- ai_engine/configs/label_encoder.json
- ai_engine/configs/emotion_mapping.json
- ai_engine/configs/sentiment_mapping.json

Legacy/non-authoritative for current 5-class model outputs:

- ai_engine/configs/labels.json

Notes:

1. labels.json contains expanded labels such as Stress, Anxiety, Loneliness, Burned Out, Hopelessness.
2. Current training/evaluation output classes are constrained by label_encoder.json to 5 classes.
3. sentiment_mapping.json still includes extra keys, but preprocessing emits canonical emotions after map_emotion, so active training labels remain canonical.

## End-to-End Summary

Emotion labels originate in dataset-specific raw fields, are normalized by emotion_mapping into five canonical classes, validated against label_encoder, encoded to numeric IDs for model training/evaluation, then decoded back to class names at inference using the same encoder mapping.

This provides a single consistent label contract across preprocessing -> training -> evaluation -> inference.
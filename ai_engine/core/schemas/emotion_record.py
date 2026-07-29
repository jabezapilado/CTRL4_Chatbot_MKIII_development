from dataclasses import dataclass, asdict


@dataclass
class EmotionRecord:

    id: str

    text: str

    original_emotion: str

    emotion: str

    sentiment: str

    is_negative: bool

    source: str

    def to_dict(self):
        return asdict(self)
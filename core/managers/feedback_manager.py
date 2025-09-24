import json
from pathlib import Path
from datetime import datetime
from config import FEEDBACKS_PATH

class FeedbackManager:
    def __init__(self, path: str = FEEDBACKS_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, question: str, model_answer: str, relevant: bool, correction: str = None, extra: dict = None):
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "question": question,
            "model_answer": model_answer,
            "relevant": bool(relevant),
            "correction": correction,
            "extra": extra or {}
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry
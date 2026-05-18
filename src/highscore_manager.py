import json
import os
import re
from typing import Any


class HighscoreManager:
    def __init__(self, filename: str = "highscores.json") -> None:
        self.filename = filename

    def load_scores(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def validate_name(name: str) -> str:
        """Validate player name: alphanumeric + spaces only, max 10 chars."""
        cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", name).strip()
        return cleaned[:10] if cleaned else "Anonymous"

    def save_score(self, score: int, name: str = "Anonymous") -> None:
        if not isinstance(score, int) or score < 0:
            print(f"Warning: invalid score '{score}', skipping save.")
            return

        validated_name = self.validate_name(name)

        scores = self.load_scores()

        scores.append({
            "name": validated_name,
            "score": score,
        })

        scores = sorted(
            scores,
            key=lambda x: x.get("score", 0),
            reverse=True,
        )[:10]

        try:
            with open(self.filename, "w") as f:
                json.dump(scores, f, indent=4)
        except IOError as e:
            print(f"Warning: could not save highscores: {e}")

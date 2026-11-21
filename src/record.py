from __future__ import annotations

from dataclasses import dataclass


def answer_points(correct: bool, used_hint: bool) -> int:
    if not correct:
        return 0
    return 3 if used_hint else 5


@dataclass
class RoundRecord:
    played_at: str
    question_count: int
    score: int
    correct_count: int | None = None
    hints_used: int | None = None

    def is_new_best(self, best_score: int | None) -> bool:
        return best_score is None or self.score > best_score

    @classmethod
    def from_dict(cls, raw: object) -> RoundRecord:
        if not isinstance(raw, dict):
            raise ValueError("한 판의 기록은 객체 형식이어야 합니다.")

        played_at = raw.get("played_at")
        question_count = raw.get("question_count")
        score = raw.get("score")
        if not isinstance(played_at, str) or not played_at.strip():
            raise ValueError("플레이 시각은 비어 있지 않은 문자열이어야 합니다.")
        if type(question_count) is not int or question_count < 1:
            raise ValueError("문항 수는 1 이상의 정수여야 합니다.")
        if type(score) is not int or not 0 <= score <= 5 * question_count:
            raise ValueError(f"한 판의 점수는 0~{5 * question_count} 사이의 정수여야 합니다.")
        for key, label in (("correct_count", "정답 수"), ("hints_used", "힌트 사용 횟수")):
            value = raw.get(key)
            if value is not None and (
                type(value) is not int or not 0 <= value <= question_count
            ):
                raise ValueError(f"{label}는 0~{question_count} 사이의 정수여야 합니다.")

        return cls(
            played_at=played_at,
            question_count=question_count,
            score=score,
            correct_count=raw.get("correct_count"),
            hints_used=raw.get("hints_used"),
        )

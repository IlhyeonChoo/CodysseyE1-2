import json
from dataclasses import asdict
from pathlib import Path
from shutil import copymode
from tempfile import NamedTemporaryFile

from .quiz import Quiz
from .record import RoundRecord

GAME_DATA_FILE = Path(__file__).resolve().parent.parent / "state.json"


class DataController:
    def __init__(self, path: Path = GAME_DATA_FILE) -> None:
        self.path = path

    def load(self) -> tuple[list[Quiz], int | None, list[RoundRecord]]:
        with self.path.open(encoding="utf-8") as source:
            try:
                data = json.load(source)
            except RecursionError as exc:
                raise ValueError("저장 데이터의 중첩 단계가 너무 많습니다.") from exc

        if not isinstance(data, dict) or not isinstance(data.get("quizzes"), list):
            raise ValueError("저장 데이터에는 퀴즈 목록이 있어야 합니다.")
        if "best_score" not in data:
            raise ValueError("저장 데이터에 최고 점수 항목이 없습니다.")
        best_score = data["best_score"]
        if best_score is not None and (type(best_score) is not int or best_score < 0):
            raise ValueError("최고 점수는 0 이상의 정수이거나 미기록 상태여야 합니다.")
        history = data.get("records", [])
        if not isinstance(history, list):
            raise ValueError("게임 기록은 목록 형식이어야 합니다.")

        quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
        records = [RoundRecord.from_dict(item) for item in history]
        if any(best_score is None or record.score > best_score for record in records):
            raise ValueError("게임 기록의 점수와 저장된 최고 점수가 맞지 않습니다.")
        return quizzes, best_score, records

    def save(
        self, quizzes: list[Quiz], best_score: int | None, records: list[RoundRecord]
    ) -> None:
        state = {
            "quizzes": [asdict(quiz) for quiz in quizzes],
            "best_score": best_score,
            "records": [asdict(record) for record in records],
        }
        # 임시 파일에 데이터를 모두 쓰고 파일을 닫은 뒤 기존 저장 파일을 교체한다.
        pending = None
        try:
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent, delete=False
            ) as output:
                pending = Path(output.name)
                json.dump(state, output, ensure_ascii=False, indent=2)
                output.write("\n")
            try:
                copymode(self.path, pending)
            except FileNotFoundError:
                pass
            pending.replace(self.path)
        finally:
            if pending is not None:
                pending.unlink(missing_ok=True)

import errno
import random
from datetime import date, datetime

from .data_control import DataController
from .quiz import Quiz, default_quizzes
from .record import RoundRecord, answer_points


def parse_number(text: str, maximum: int) -> int | None:
    """입력값이 허용 범위 안의 숫자면 반환하고, 그렇지 않으면 범위를 안내한다."""
    try:
        number = int(text.strip())
        if 1 <= number <= maximum:
            return number
    except ValueError:
        pass
    print(f"1~{maximum} 사이의 숫자를 입력하세요.")
    return None


def read_number(prompt: str, maximum: int) -> int:
    while True:
        number = parse_number(input(prompt), maximum)
        if number is not None:
            return number


def read_text(prompt: str) -> str:
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("내용을 입력하세요.")


def confirm(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} (예/아니요) > ").strip().lower()
        if answer in ("예", "yes"):
            return True
        if answer in ("아니요", "no"):
            return False
        print("예 또는 아니요를 입력하세요.")


def read_answer(quiz: Quiz) -> tuple[int, bool]:
    used_hint = False
    while True:
        text = input("정답 번호(1~4) 또는 ‘힌트’를 입력하세요 > ").strip()
        if text.lower() in ("힌트", "h"):
            if not used_hint:
                hint = quiz.hint
                if not hint:
                    wrong = random.choice([i for i in range(1, 5) if i != quiz.answer])
                    hint = f"{wrong}번 선택지는 오답입니다."
                print(f"힌트: {hint} (정답 시 3점)")
                used_hint = True
            else:
                print("이 문항의 힌트를 이미 사용했습니다.")
            continue
        answer = parse_number(text, 4)
        if answer is not None:
            return answer, used_hint


def file_error_message(error: OSError) -> str:
    messages = {
        errno.EACCES: "파일에 접근할 권한이 없습니다.",
        errno.EPERM: "파일에 접근할 권한이 없습니다.",
        errno.ENOENT: "파일이나 폴더를 찾을 수 없습니다.",
        errno.EISDIR: "저장 파일 위치에 폴더가 있습니다.",
        errno.ENOTDIR: "파일 경로에 지정한 폴더를 찾을 수 없습니다.",
        errno.ENOSPC: "저장 공간이 부족합니다.",
        errno.EROFS: "읽기 전용 저장 장치입니다.",
    }
    if error.errno is None:
        return "파일 경로와 접근 권한을 확인하세요."
    return messages.get(error.errno, f"운영 체제 오류 번호는 {error.errno}입니다.")


class QuizGame:
    def __init__(self, store: DataController | None = None) -> None:
        self.store = DataController() if store is None else store
        self.quizzes: list[Quiz] = []
        self.best_score: int | None = None
        self.records: list[RoundRecord] = []
        self._dirty = False

    def _load(self) -> bool:
        try:
            self.quizzes, self.best_score, self.records = self.store.load()
            return True
        except FileNotFoundError:
            print("저장 파일이 없어 기본 컴퓨터 과학 퀴즈로 시작합니다.")
        except ValueError:
            print("저장 파일의 내용이 손상되어 기본 컴퓨터 과학 퀴즈로 복구합니다.")
        except OSError as exc:
            print(f"저장 파일을 읽을 수 없어 종료합니다. {file_error_message(exc)}")
            return False

        self.quizzes = default_quizzes()
        self.best_score = None
        self.records = []
        self._dirty = True
        return True

    def _save(self) -> None:
        self._dirty = True
        try:
            self.store.save(self.quizzes, self.best_score, self.records)
        except OSError as exc:
            print(f"게임 데이터 저장에 실패했습니다. {file_error_message(exc)}")
        except UnicodeError:
            print("게임 데이터 저장에 실패했습니다. 저장할 수 없는 문자가 있습니다.")
        else:
            self._dirty = False

    def play(self, random_order: bool = False) -> None:
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        questions = self.quizzes
        if random_order:
            count = read_number(f"풀 문항 수 (1~{len(questions)}) > ", len(questions))
            questions = random.sample(questions, count)

        correct_count = hints_used = score = 0
        for index, quiz in enumerate(questions, start=1):
            print(f"\n[문제 {index}/{len(questions)}]")
            quiz.display()
            answer, used_hint = read_answer(quiz)
            correct = quiz.is_correct(answer)
            points = answer_points(correct, used_hint)
            if correct:
                correct_count += 1
                print(f"정답입니다! (+{points}점)")
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")
            if quiz.explanation:
                print(f"해설: {quiz.explanation}")
            hints_used += int(used_hint)
            score += points

        record = RoundRecord(
            played_at=datetime.now().astimezone().isoformat(timespec="seconds"),
            question_count=len(questions),
            score=score,
            correct_count=correct_count,
            hints_used=hints_used,
        )
        new_best = record.is_new_best(self.best_score)
        if new_best:
            self.best_score = score
        self.records.append(record)
        self._save()
        print(f"결과: {len(questions)}문제 중 {correct_count}문제 정답, 총 {score}점")
        if new_best:
            print("새로운 최고 점수입니다!")

    def add_quiz(self) -> None:
        question = read_text("등록할 문제 > ")
        choices = [read_text(f"선택지 {i} > ") for i in range(1, 5)]
        answer = read_number("정답 번호 (1~4) > ", 4)
        quiz = Quiz(question, choices, answer, created_at=date.today().isoformat())
        print("\n[등록할 퀴즈]")
        quiz.display()
        print(f"정답: {answer}번")
        if confirm("이 퀴즈를 등록할까요?"):
            self.quizzes.append(quiz)
            self._save()
            print("퀴즈를 등록했습니다.")
        else:
            print("등록을 취소했습니다.")

    def show_quizzes(self) -> None:
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        print(f"\n퀴즈 목록 ({len(self.quizzes)}문제)")
        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"[{index}] {quiz.question}")

    def delete_quiz(self) -> None:
        self.show_quizzes()
        if not self.quizzes:
            return
        index = read_number("삭제할 퀴즈 번호 > ", len(self.quizzes)) - 1
        if confirm(f"‘{self.quizzes[index].question}’ 문항을 삭제할까요?"):
            self.quizzes.pop(index)
            self._save()
            print("퀴즈를 삭제했습니다.")
        else:
            print("삭제를 취소했습니다.")

    def show_scores(self) -> None:
        if self.best_score is None:
            print("아직 완료한 게임 기록이 없습니다.")
            return
        print(f"최고 점수: {self.best_score}점")
        if self.records:
            print("풀이 기록 (최근 순)")
        for record in reversed(self.records):
            try:
                played_at = datetime.fromisoformat(record.played_at).strftime(
                    "%Y년 %m월 %d일 %H시 %M분 %S초 %z"
                ).rstrip()
            except ValueError:
                played_at = record.played_at
            detail = f"{record.question_count}문제"
            if record.correct_count is not None:
                wrong_count = record.question_count - record.correct_count
                detail += f" / 정답 {record.correct_count}개 / 오답 {wrong_count}개"
            if record.hints_used is not None:
                detail += f" / 힌트 {record.hints_used}회"
            print(f"{played_at}  {detail}  {record.score}점")

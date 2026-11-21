from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Quiz:
    question: str
    choices: list[str]
    answer: int
    hint: str = ""
    explanation: str = ""
    created_at: str = ""

    def display(self) -> None:
        print(self.question)
        for number, choice in enumerate(self.choices, start=1):
            print(f"  {number}. {choice}")

    def is_correct(self, choice: int) -> bool:
        return self.answer == choice

    @classmethod
    def from_dict(cls, raw: object) -> Quiz:
        if not isinstance(raw, dict):
            raise ValueError("각 퀴즈는 문제와 선택지, 정답을 담은 객체여야 합니다.")
        question = raw.get("question")
        choices = raw.get("choices")
        answer = raw.get("answer")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제에는 한 글자 이상의 내용이 있어야 합니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 네 개여야 합니다.")
        if not all(isinstance(item, str) and item.strip() for item in choices):
            raise ValueError("각 선택지에는 한 글자 이상의 내용이 있어야 합니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답 번호는 1부터 4까지의 정수여야 합니다.")

        optional = {}
        for key, label in (("hint", "힌트"), ("explanation", "해설"), ("created_at", "등록일")):
            value = raw.get(key, "")
            if not isinstance(value, str):
                raise ValueError(f"{label} 항목은 문자열이어야 합니다.")
            optional[key] = value.strip()
        return cls(
            question.strip(), [item.strip() for item in choices], answer, **optional
        )


def default_quizzes() -> list[Quiz]:
    """첫 실행이나 저장 파일 복구에 사용할 기본 컴퓨터 과학 문항을 만든다."""
    return [
        Quiz(
            "스택에 ‘가’, ‘나’, ‘다’를 차례로 넣은 뒤 한 번 꺼내면 어떤 값이 나올까요?",
            ["가", "나", "다", "세 값이 한꺼번에 나온다"],
            3,
            "접시를 쌓았다가 맨 위에서 한 장 꺼내는 상황을 떠올려 보세요.",
            "스택은 마지막에 넣은 값을 먼저 꺼내므로 ‘다’가 나옵니다.",
        ),
        Quiz(
            "정렬된 배열에서 이진 탐색이 한 번 비교할 때마다 줄이는 것은 무엇일까요?",
            ["탐색할 범위", "각 원소의 값", "배열의 실제 길이", "원소의 저장 공간"],
            1,
            "가운데 원소와 목표값을 비교한 뒤 어느 쪽을 계속 볼지 결정합니다.",
            "목표값이 있을 수 없는 절반을 탐색 범위에서 제외합니다.",
        ),
        Quiz(
            "컴퓨터의 전원을 끄면 저장한 내용이 사라지는 장치는 무엇일까요?",
            ["솔리드 스테이트 드라이브", "하드 디스크", "휴대용 플래시 메모리", "디램"],
            4,
            "프로그램 실행 중 작업 공간으로 쓰이는 휘발성 메모리입니다.",
            "디램은 휘발성 메모리이므로 전원이 끊기면 저장한 내용이 사라집니다.",
        ),
        Quiz(
            "브라우저가 도메인 이름으로 서버의 네트워크 주소를 조회할 때 쓰는 시스템은 무엇일까요?",
            ["웹 문서 전송 규약", "도메인 이름 시스템", "웹 문서 작성 언어", "유니코드 문자 인코딩 방식"],
            2,
            "인터넷에서 이름에 대응하는 주소를 조회하는 역할입니다.",
            "도메인 이름 시스템에서 도메인의 주소 레코드를 조회하면 서버의 네트워크 주소를 알 수 있습니다.",
        ),
        Quiz(
            "두 계좌의 잔액 변경을 모두 반영하거나 모두 취소하게 하는 트랜잭션의 성질은 무엇일까요?",
            ["원자성", "가용성", "압축성", "확장성"],
            1,
            "송금의 출금과 입금을 하나의 작업 단위로 취급합니다.",
            "원자성은 트랜잭션의 작업이 전부 적용되거나 전부 취소되도록 보장합니다.",
        ),
    ]

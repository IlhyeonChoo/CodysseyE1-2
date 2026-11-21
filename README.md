# 컴퓨터 과학 퀴즈 게임

터미널에서 컴퓨터 과학 객관식 퀴즈를 풀고 새 문항을 등록하는 파이썬 프로그램입니다. 기본 14문항은 자료구조와 알고리즘, 컴퓨터 구조, 운영체제, 네트워크, 데이터베이스, 이산수학과 형식 언어를 다룹니다. 추가한 문항과 최고 점수, 풀이 기록은 게임을 종료한 뒤에도 유지됩니다.

## 주제 선정 이유

코디세이에서 인공지능을 활용해 소프트웨어를 개발할 때, 컴퓨터 과학의 기초를 알고 있으면 더 효율적으로 문제를 풀 수 있다고 생각했습니다. 그래서 소프트웨어 개발에 필요한 기초 개념을 퀴즈 주제로 골랐습니다.

## 실행 방법

Python 3.10 이상이 필요하며 표준 라이브러리만 사용합니다. 저장소를 내려받고 `README.md`가 있는 디렉터리에서 실행하세요.

```bash
python3 src/main.py
```

`uv`를 사용하는 경우 다음 명령으로 Python 3.11에서 실행할 수 있습니다.

```bash
uv run --no-project --python 3.11 python -m src.main
```

회귀 테스트는 `python3 -m unittest discover -s tests -v`로 실행합니다. 테스트 데이터는 임시 디렉터리에 저장합니다.

## 기능 목록

| 번호 | 기능 | 사용 방법 |
| --- | --- | --- |
| 1 | 퀴즈 풀기 | 등록된 순서대로 모든 문항을 풉니다. 정답 번호는 1~4이고, `힌트`를 입력하면 힌트를 봅니다. |
| 2 | 퀴즈 등록 | 문제, 선택지 4개, 정답 번호를 입력합니다. 미리보기를 확인하고 `예`를 입력하면 저장하고, `아니요`를 입력하면 취소합니다. |
| 3 | 퀴즈 목록 | 등록된 순서대로 번호와 문제를 확인합니다. |
| 4 | 점수 확인 | 최고 점수와 완료한 라운드의 기록을 최근 순서로 확인합니다. |
| 5 | 종료 | 저장을 마치고 게임을 종료합니다. |
| 6 | 무작위 퀴즈 풀기 | 풀 문항 수를 선택하면 중복 없이 무작위로 출제합니다. |
| 7 | 퀴즈 삭제 | 목록 번호로 문항을 선택하고 `예`로 확인하면 삭제합니다. |

정답은 5점, 힌트를 보고 맞히면 3점, 오답은 0점입니다. 예를 들어 세 문항 중 한 문항을 바로 맞히고 한 문항을 힌트로 맞히면 총 8점입니다. 최고 점수는 끝까지 푼 한 판의 총점으로 비교하며, 동점이면 먼저 달성한 기록을 유지합니다.

빈 입력이나 범위 밖의 번호를 입력하면 같은 항목을 다시 묻습니다. 읽을 수 없는 문자가 섞인 경우에도 해당 줄만 다시 입력하면 됩니다. 예를 들어 두 번째 선택지에서 오류가 나면 문제와 첫 번째 선택지는 그대로 유지됩니다. `Ctrl+C`를 누르거나 입력이 끝나면 게임을 종료합니다. 이때 확인 전인 문항이나 풀이 중인 판은 기록에서 제외됩니다.

## 파일 구조

```text
.
├── README.md
├── state.json           퀴즈, 최고 점수, 풀이 기록
├── docs/                미션 요구사항, 프로그램 설계와 흐름
├── src/
│   ├── __init__.py
│   ├── main.py          게임을 시작하는 진입점
│   ├── game.py          QuizGame 클래스와 메뉴, 입력, 라운드 진행
│   ├── quiz.py          Quiz 클래스와 복구에 쓰는 기본 문항
│   ├── record.py        문항별 채점과 완료한 라운드 기록
│   └── data_control.py  저장 파일 읽기, 형식 검증, 쓰기
└── tests/
    └── test_game.py     게임 진행과 저장 동작 테스트
```

## 데이터 파일 `state.json`

실행 디렉터리에 관계없이 저장소 루트의 `state.json`을 UTF-8로 읽고 씁니다.

| 필드 | 내용 |
| --- | --- |
| `quizzes` | 문항 목록입니다. 각 문항에는 문제 `question`, 선택지 4개 `choices`, 정답 번호 `answer`(1~4)가 필요합니다. 힌트 `hint`, 해설 `explanation`, 등록일 `created_at`은 선택 항목입니다. |
| `best_score` | 완료한 라운드의 최고 점수입니다. 첫 플레이 전에는 `null`, 한 판을 완료해 얻은 0점은 `0`입니다. |
| `records` | 완료 순서대로 플레이 시각 `played_at`, 문항 수 `question_count`, 총점 `score`를 저장합니다. 새 기록에는 정답 수 `correct_count`, 힌트를 본 문항 수 `hints_used`도 포함됩니다. |

한 문항만 담은 저장 형식 예시입니다. `answer`가 `3`이므로 세 번째 선택지인 ‘다’가 정답입니다.

```json
{
  "quizzes": [
    {
      "question": "스택에 ‘가’, ‘나’, ‘다’를 차례로 넣은 뒤 한 번 꺼내면 어떤 값이 나올까요?",
      "choices": ["가", "나", "다", "세 값이 한꺼번에 나온다"],
      "answer": 3
    }
  ],
  "best_score": null,
  "records": []
}
```

문항 등록·삭제를 확정하거나 한 판을 끝내면 즉시 저장합니다. 저장에 실패하면 변경 내용을 메모리에 두고 다음 저장 시점이나 종료 시 다시 시도합니다.

파일이 없거나 내용이 손상되면 기본 문항과 빈 점수 기록으로 시작합니다. 직접 모든 문항을 삭제해 저장한 빈 목록은 그대로 유지합니다. 읽기 권한 등의 문제로 파일을 열 수 없으면 원인을 안내하고 종료합니다.

## 미션 제출 자료

제출할 공개 저장소는 [IlhyeonChoo/CodysseyE1-2](https://github.com/IlhyeonChoo/CodysseyE1-2)입니다.

### 개발 환경과 실행 화면

아래 파일명으로 PNG를 `docs/screenshots/`에 저장하면 각 항목을 펼쳐 화면을 볼 수 있습니다.

<details>
<summary>개발 환경 · environment.png</summary>

프로젝트를 연 편집기와 터미널에서 실행한 `python3 --version`, `git --version`, `git config --get user.name` 결과를 함께 담습니다.

![편집기와 파이썬 버전, Git 설정](docs/screenshots/environment.png)

</details>

<details>
<summary>퀴즈 등록 · add_quiz.png</summary>

메뉴 2에서 문제, 선택지 4개, 정답 번호를 입력합니다. 미리보기와 `예` 입력 후 등록 완료 메시지가 한 화면에 보이도록 캡처합니다.

![새 퀴즈의 입력 내용과 등록 완료 메시지](docs/screenshots/add_quiz.png)

</details>

<details>
<summary>퀴즈 목록 · list.png</summary>

메뉴 3에서 방금 등록한 문제의 번호와 제목을 확인합니다.

![추가한 문항이 포함된 퀴즈 목록](docs/screenshots/list.png)

</details>

<details>
<summary>퀴즈 풀이 · play.png</summary>

메뉴 6에서 한 문항을 선택해 끝까지 풉니다. 문제와 선택지, 입력한 답의 채점 결과, 한 판의 총점을 담습니다. 메뉴 1에서 전체 문항을 풀어도 됩니다.

![문항과 선택지, 채점 결과와 총점](docs/screenshots/play.png)

</details>

<details>
<summary>재실행 후 점수 확인 · score.png</summary>

메뉴 5로 종료한 뒤 다시 실행합니다. 메뉴 4에서 최고 점수와 방금 끝낸 판의 기록을 확인합니다. 메뉴 3에서는 추가한 문항도 다시 볼 수 있습니다.

![재실행 후 표시되는 최고 점수와 풀이 기록](docs/screenshots/score.png)

</details>

### Git 복제 실습과 이력

1. 원본 저장소의 `main`에 완성본을 푸시한 뒤, 원본 루트에서 아래 명령으로 별도의 실습 디렉터리를 만듭니다.

   ```bash
   git clone git@github.com:IlhyeonChoo/CodysseyE1-2.git ../CodysseyE1-2-practice
   cd ../CodysseyE1-2-practice
   mkdir -p docs/screenshots
   python3 src/main.py
   ```

2. **복제본**에서 위의 다섯 화면을 캡처해 지정된 파일명으로 저장합니다. 캡처 파일을 커밋해 푸시하고, `git log -1 --oneline`에 나오는 커밋 번호를 확인합니다.

   ```bash
   git add -- docs/screenshots/
   git commit -m "docs: add environment and quiz screenshots"
   git push origin main
   git log -1 --oneline
   ```

3. **원본**으로 돌아와 변경을 받습니다. 복제본에서 본 커밋 번호와 원본의 커밋 번호가 같고, 사진 다섯 장이 들어왔는지 확인합니다.

   ```bash
   cd ../CodysseyE1-2
   git pull --ff-only origin main
   git log -1 --oneline
   ls docs/screenshots/
   git log --oneline --graph
   ```

<details>
<summary>브랜치 병합과 커밋 그래프 · git-graph.png</summary>

마지막 명령의 출력에서 퀴즈 기능 브랜치가 `main`에 합쳐지는 지점과 기능별 커밋이 보이도록 캡처합니다.

![기능 브랜치 병합과 커밋 이력](docs/screenshots/git-graph.png)

</details>

복제 실습 로그도 첨부하려면 복제본의 푸시 결과, 원본의 풀 결과, 양쪽의 커밋 번호를 `docs/clone-pull.txt`에 저장합니다. [실습 자료 폴더](docs/)

4. **원본**에서 그래프 캡처를 커밋하고 푸시합니다. 선택 로그를 작성했다면 커밋 전에 `git add -- docs/clone-pull.txt`도 실행합니다.

   ```bash
   git add -- docs/screenshots/git-graph.png
   git commit -m "docs: add submission evidence for Git history"
   git push origin main
   ```

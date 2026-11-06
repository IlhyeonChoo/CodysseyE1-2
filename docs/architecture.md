# 전체 파일
1. quiz.py
2. game.py
3. record.py
4. state.json

# 1. quiz.py
퀴즈 클래스 정의 및 퀴즈의 메서드들 정의



# 2. game.py
게임 전체 조작
어떤 작업을 수행할지 입력받아 해당 클래스나 메서드로 전달
main 역할 담당

# 3. record.py
유저의 기록과 관련된 클래스
기록을 불러오거나 최고 기록을 체크하는 등의 작업

# 4. state.json
퀴즈나 기록 데이터를 저장해둔 데이터 파일

```json
{
    "quiz" : [
        {
            "id" : "int",
            "question" : "string",
            "option" : [
                "1" : "string",
                "2" : "string",
                "3" : "string",
                "4" : "string"
            ],
            "answer" : "int",
            "hint" : "string",
            "explain" : "string",
            "date" : "MM-DD-YYYY"
        },
    ],
    "record" : [
        {
            "score" : "int",
            "date" : "MM-DD-YYYY",
            "quizNum" : "int",
            "correctNum" : "int",
            "wrongNum" : "int",
            "useHintNum" : "int",
        },
    ],
    "bestRecord" : {
        "score" : "int",
        "date" : "MM-DD-YYYY",
        "quizNum" : "int",
        "correctNum" : "int",
        "wrongNum" : "int",
        "useHintNum" : "int"
    }
}
```


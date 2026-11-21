if __package__:
    from .game import QuizGame
else:
    import sys
    from pathlib import Path

    # 파일을 직접 실행할 때도 패키지를 찾도록 프로젝트 루트를 검색 경로에 추가한다.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.game import QuizGame

if __name__ == "__main__":
    QuizGame().run()

import errno
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src.data_control import DataController
from src.game import QuizGame
from src.quiz import default_quizzes


class GameTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "state.json"
        self.store = DataController(self.path)

    def run_game(self, inputs):
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(inputs)), redirect_stdout(output):
            QuizGame(self.store).run()
        return output.getvalue()

    def test_cli_saves_in_project_root_and_loads_registration_after_restart(self):
        source = Path(__file__).resolve().parents[1] / "src"
        shutil.copytree(
            source, self.root / "src", ignore=shutil.ignore_patterns("__pycache__")
        )
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        command = [sys.executable, str(self.root / "src/main.py")]
        subprocess.run(
            command, cwd=elsewhere, input="2\n  새 문항  \n가\n나\n다\n라\n3\n예\n5\n",
            text=True, capture_output=True, check=True, timeout=5,
        )
        quizzes, best, records = self.store.load()
        self.assertEqual(len(quizzes), len(default_quizzes()) + 1)
        self.assertEqual((quizzes[-1].question, quizzes[-1].answer), ("새 문항", 3))
        self.assertIsNone(best)
        self.assertEqual(records, [])
        self.assertFalse((elsewhere / "state.json").exists())
        result = subprocess.run(
            command, cwd=elsewhere, input="3\n5\n", text=True,
            capture_output=True, check=True, timeout=5,
        )
        self.assertIn("새 문항", result.stdout)

    def test_empty_legacy_state_and_cancelled_or_interrupted_registration(self):
        original = '{"quizzes": [], "best_score": null}'
        self.path.write_text(original, encoding="utf-8")
        output = self.run_game(
            "\nabc\n9\n 1 \n3\n4\n6\n7\n"
            "2\n \n문제\n가\n나\n다\n라\n0\n2\n모름\n아니요\n2\n미완성\n"
        )
        self.assertGreaterEqual(output.count("등록된 퀴즈가 없습니다"), 4)
        self.assertIn("완료한 게임 기록이 없습니다", output)
        self.assertIn("예 또는 아니요", output)
        self.assertIn("등록을 취소", output)
        self.assertIn("입력이 중단", output)
        self.assertEqual(self.path.read_text(encoding="utf-8"), original)

    def test_damaged_files_recover_with_default_quizzes(self):
        invalid_quiz = {
            "question": "문항", "choices": ["a", "b", "c", "d"], "answer": True
        }
        for invalid in (
            b"", b"\xff", b"{", b"[]", b'{"quizzes": []}',
            b'{"quizzes": [], "best_score": false}',
            json.dumps({"quizzes": [invalid_quiz], "best_score": None}).encode(),
        ):
            with self.subTest(invalid=invalid):
                self.path.write_bytes(invalid)
                self.assertIn("손상", self.run_game("5\n"))
                self.assertEqual(self.store.load(), (default_quizzes(), None, []))

    def test_completed_rounds_score_hints_ties_and_midround_eof(self):
        quiz = default_quizzes()[0]
        self.store.save([quiz], None, [])
        wrong = quiz.answer % 4 + 1
        self.run_game(f"1\n{wrong}\n5\n")
        _, best, records = self.store.load()
        self.assertEqual(best, 0)
        first = records[0]
        self.assertIn("최고 점수: 0점", self.run_game("4\n5\n"))
        output = self.run_game(
            f"1\n힌트\n힌트\n{quiz.answer}\n1\nh\n{quiz.answer}\n"
            f"1\n{quiz.answer}\n1\n{wrong}\n1\nh\n"
        )
        _, best, records = self.store.load()
        self.assertEqual(records[0], first)
        self.assertEqual(best, 5)
        self.assertEqual([record.score for record in records], [0, 3, 3, 5, 0])
        self.assertEqual(records[1].hints_used, 1)
        self.assertEqual(output.count("새로운 최고 점수"), 2)

    def test_random_sample_and_confirmed_deletion(self):
        quizzes = default_quizzes()
        self.store.save(quizzes, None, [])
        output = self.run_game("6\n0\n3\n1\n1\n1\n5\n")
        self.assertEqual(sum(quiz.question in output for quiz in quizzes), 3)
        self.assertEqual(self.store.load()[2][0].question_count, 3)
        self.run_game("7\n2\nno\n7\n1\n예\n5\n")
        self.assertEqual(self.store.load()[0], quizzes[1:])

    def test_partial_write_keeps_original_file_until_retry(self):
        self.store.save([], None, [])
        original = self.path.read_bytes()
        dump = json.dump
        attempts = 0

        def fail_first(state, stream, **options):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                stream.write("{")
                raise OSError(errno.ENOSPC, "No space left on device")
            self.assertEqual(self.path.read_bytes(), original)
            dump(state, stream, **options)

        with patch("src.data_control.json.dump", side_effect=fail_first):
            output = self.run_game("2\n문제\n가\n나\n다\n라\n1\nyes\n3\n")
        self.assertIn("저장에 실패", output)
        self.assertIn("저장 공간이 부족합니다", output)
        self.assertNotIn("No space left on device", output)
        self.assertIn("[1] 문제", output)
        self.assertEqual(attempts, 2)
        self.assertEqual(self.store.load()[0][0].question, "문제")
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_read_error_exits_without_trying_to_replace_state(self):
        self.path.mkdir()
        with patch.object(self.store, "save") as save:
            self.assertIn("읽을 수 없어", self.run_game(""))
            save.assert_not_called()
        self.assertTrue(self.path.is_dir())

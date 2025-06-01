import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_scaffold_files_exist_and_importable():
    files = ['app.py', 'tutor.py', 'data_manager.py', 'plan.md', 'ticket1.md']
    for fname in files:
        assert os.path.isfile(fname), f"Expected {fname} to exist"
    import app
    import tutor
    import data_manager


def test_initial_json_structure():
    from data_manager import VOCAB_FILE, MEMORY_FILE, CHAT_SESSIONS_FILE

    vocab = json.loads(VOCAB_FILE.read_text(encoding='utf-8'))
    assert vocab == []

    memory = json.loads(MEMORY_FILE.read_text(encoding='utf-8'))
    assert isinstance(memory, dict) and memory == {}

    sessions = json.loads(CHAT_SESSIONS_FILE.read_text(encoding='utf-8'))
    assert isinstance(sessions, dict) and sessions == {}
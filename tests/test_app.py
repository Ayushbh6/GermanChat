import sys
import os

# Ensure project root on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from datetime import date, datetime

import pytest

import app
import data_manager
import tutor


class DummyColumn:
    """Dummy column to capture UI calls in run_flashcards."""
    def __init__(self):
        self.subheaders = []
        self.writes = []

    def subheader(self, txt):
        self.subheaders.append(txt)

    def write(self, obj):
        self.writes.append(obj)

    def button(self, label, key=None, **kwargs):
        # default stub; override in tests as needed
        return False


def test_main_mode_selector(monkeypatch):
    calls = []
    monkeypatch.setattr(app.st.sidebar, 'title', lambda t: None)
    monkeypatch.setattr(app.st.sidebar, 'radio', lambda label, options: 'Flashcards')
    monkeypatch.setattr(app, 'run_chat_tutor', lambda: calls.append('chat'))
    monkeypatch.setattr(app, 'run_flashcards', lambda: calls.append('flash'))
    app.main()
    assert calls == ['flash']


def test_run_chat_tutor_session(monkeypatch):
    selected = []
    monkeypatch.setattr(data_manager, 'list_sessions', lambda: ['s1'])
    monkeypatch.setattr(app.st.sidebar, 'selectbox', lambda label, options: 's1')
    monkeypatch.setattr(data_manager, 'load_session', lambda sid: selected.append(sid) or [])
    # stub UI to skip actions
    monkeypatch.setattr(app.st, 'button', lambda *args, key=None, **kwargs: False)
    monkeypatch.setattr(app.st, 'text_input', lambda *args, key=None, **kwargs: '')
    app.run_chat_tutor()
    assert selected == ['s1']


def test_run_chat_tutor_send(monkeypatch):
    monkeypatch.setattr(data_manager, 'list_sessions', lambda: ['s1'])
    monkeypatch.setattr(app.st.sidebar, 'selectbox', lambda label, options: 's1')
    monkeypatch.setattr(data_manager, 'load_session', lambda sid: [])
    # simulate user input and send click
    monkeypatch.setattr(app.st, 'text_input', lambda label, key=None: 'Hello')
    def fake_button(label, key=None, **kwargs):
        return key == 'send'
    monkeypatch.setattr(app.st, 'button', fake_button)
    called = []
    monkeypatch.setattr(tutor, 'chat_session_interact', lambda sid, msg: called.append((sid, msg)) or 'Reply')
    outputs = []
    monkeypatch.setattr(app.st, 'markdown', lambda txt: outputs.append(txt))
    app.run_chat_tutor()
    assert called == [('s1', 'Hello')]
    assert outputs == ['**Tutor:** Reply']


def test_run_chat_tutor_teach_and_quiz(monkeypatch):
    monkeypatch.setattr(data_manager, 'list_sessions', lambda: [])
    monkeypatch.setattr(app.st.sidebar, 'selectbox', lambda label, options: 'New Session')
    monkeypatch.setattr(data_manager, 'load_session', lambda sid: [])
    teach_called = []
    quiz_called = []
    monkeypatch.setattr(tutor, 'generate_new_batch', lambda n: teach_called.append(n) or ['w'])
    monkeypatch.setattr(tutor, 'prepare_quiz', lambda n: quiz_called.append(n) or [{'root': 'r', 'distractors': [], 'expected_answer': 'e'}])
    # stub random.shuffle
    monkeypatch.setattr(random, 'shuffle', lambda x: x)
    def fake_button(label, key=None, **kwargs):
        return key in ('teach', 'quiz')
    monkeypatch.setattr(app.st, 'button', fake_button)
    writes = []
    monkeypatch.setattr(app.st, 'write', lambda v: writes.append(v))
    monkeypatch.setattr(app.st, 'radio', lambda label, options, key=None: None)
    app.run_chat_tutor()
    assert teach_called == [20]
    assert quiz_called == [5]
    assert any('Added' in str(v) for v in writes)
    assert any('Translate:' in str(v) for v in writes)


def test_run_flashcards(monkeypatch):
    today = date.today().isoformat()
    vocab = [{
        'root': 'Haus',
        'english': 'house',
        'examples': {'present': ['Ich lerne.']},
        'last_reviewed': None,
        'known': False
    }]
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: vocab)
    saved = []
    monkeypatch.setattr(data_manager, 'save_vocab', lambda v: saved.append(v.copy()))
    dummy = DummyColumn()
    monkeypatch.setattr(app.st, 'columns', lambda n: [dummy] * n)
    # simulate show/examples and known clicks
    monkeypatch.setattr(DummyColumn, 'button', lambda self, label, key=None, **kwargs: label in ("Show Examples", "Known"))
    app.run_flashcards()
    assert dummy.subheaders == ['Haus - house']
    assert vocab[0]['examples'] in dummy.writes
    assert saved, "save_vocab should have been called"
    updated = saved[-1][0]
    assert updated['known'] is True
    assert updated['last_reviewed'] == today
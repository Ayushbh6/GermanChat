import sys
import os

# Ensure project root is on PYTHONPATH for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from datetime import date

import pytest

import tutor
import data_manager


class DummyResponse:
    def __init__(self, output_text):
        self.output_text = output_text


def test_prepare_quiz_empty_vocab(monkeypatch):
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: [])
    assert tutor.prepare_quiz(1) == []


def test_prepare_quiz_basic(monkeypatch):
    vocab = [
        {'root': 'Haus', 'english': 'house', 'taught_on': '2023-01-01', 'batch_id': 1, 'examples': {}, 'last_reviewed': None, 'known': False},
        {'root': 'Baum', 'english': 'tree', 'taught_on': '2023-01-01', 'batch_id': 1, 'examples': {}, 'last_reviewed': None, 'known': False},
        {'root': 'Wasser', 'english': 'water', 'taught_on': '2023-01-01', 'batch_id': 1, 'examples': {}, 'last_reviewed': None, 'known': False},
    ]
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: vocab)
    quiz = tutor.prepare_quiz(2)
    assert len(quiz) == 2
    for q in quiz:
        assert 'root' in q and 'expected_answer' in q and 'distractors' in q
        assert isinstance(q['distractors'], list)
        assert q['expected_answer'] not in q['distractors']
        assert all(isinstance(d, str) for d in q['distractors'])


def test_write_memory(monkeypatch):
    calls = []

    def fake_append_memory(key, entry):
        calls.append((key, entry))

    monkeypatch.setattr(data_manager, 'append_memory', fake_append_memory)
    entry = {'level': 'A1', 'notes': 'Test'}
    tutor.write_memory(entry)
    assert len(calls) == 1
    assert calls[0][0] == date.today().isoformat()
    assert calls[0][1] == entry


def test_generate_new_batch_not_due(monkeypatch):
    monkeypatch.setattr(data_manager, 'days_since_last_batch', lambda: 2)
    called = {'api': False}

    def fake_api(*args, **kwargs):
        called['api'] = True
        return DummyResponse('[]')

    monkeypatch.setattr(tutor.client.responses, 'create', fake_api)
    res = tutor.generate_new_batch(1)
    assert res == []
    assert not called['api']


def test_generate_new_batch_basic(monkeypatch):
    monkeypatch.setattr(data_manager, 'days_since_last_batch', lambda: 3)
    monkeypatch.setattr(data_manager, 'is_new_word', lambda root: True)
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: [])
    saved = []

    def fake_save(vocab_list):
        saved.extend(vocab_list)

    monkeypatch.setattr(data_manager, 'save_vocab', fake_save)

    items = [
        {
            'root': 'Haus',
            'english': 'house',
            'examples': {'past': 'Hatte ein Haus', 'present': 'Habe ein Haus', 'future': 'Werde ein Haus haben'}
        }
    ]
    monkeypatch.setattr(
        tutor.client.responses,
        'create',
        lambda *args, **kwargs: DummyResponse(json.dumps({"german_sentences": items}))
    )
    new = tutor.generate_new_batch(1)
    assert len(new) == 1
    entry = new[0]
    assert entry['root'] == 'Haus'
    assert entry['english'] == 'house'
    assert entry['examples'] == items[0]['examples']
    assert entry['batch_id'] == 1
    assert entry['taught_on'] == date.today().isoformat()
    assert entry['last_reviewed'] is None
    assert entry['known'] is False
    assert saved == new


def test_generate_new_batch_duplicate(monkeypatch):
    monkeypatch.setattr(data_manager, 'days_since_last_batch', lambda: 3)
    monkeypatch.setattr(data_manager, 'is_new_word', lambda root: False)
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: [])

    called = {'saved': False}

    def fake_save(_):
        called['saved'] = True

    monkeypatch.setattr(data_manager, 'save_vocab', fake_save)
    monkeypatch.setattr(
        tutor.client.responses,
        'create',
        lambda *args, **kwargs: DummyResponse(json.dumps({
            "german_sentences": [
                {'root': 'Haus', 'english': 'house', 'examples': {}}
            ]
        }))
    )
    res = tutor.generate_new_batch(1)
    assert res == []
    assert not called['saved']


def test_chat_session_interact(monkeypatch):
    session_id = 'test_session'
    history = [{'role': 'system', 'text': 'Welcome'}]
    trimmed = [{'role': 'system', 'text': 'Welcome'}]
    monkeypatch.setattr(data_manager, 'load_session', lambda sid: history.copy())
    monkeypatch.setattr(data_manager, 'trim_messages', lambda msgs, max_tokens=600000: trimmed)
    calls = []

    def fake_append(session, role, text):
        calls.append((session, role, text))

    monkeypatch.setattr(data_manager, 'append_message', fake_append)
    monkeypatch.setattr(
        tutor.client.responses,
        'create',
        lambda *args, **kwargs: DummyResponse('{"reply": "Hallo"}')
    )
    reply = tutor.chat_session_interact(session_id, 'Hi there')
    assert calls[0] == (session_id, 'user', 'Hi there')
    assert calls[1] == (session_id, 'assistant', '{"reply": "Hallo"}')
    assert reply == '{"reply": "Hallo"}'
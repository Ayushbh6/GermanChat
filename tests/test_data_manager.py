import sys
import os
import json
import math
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

import data_manager


def test_load_save_vocab(tmp_path, monkeypatch):
    vocab_file = tmp_path / 'vocab.json'
    monkeypatch.setattr(data_manager, 'VOCAB_FILE', vocab_file)
    assert data_manager.load_vocab() == []
    sample = [{'root': 'Haus', 'english': 'house', 'taught_on': '2023-01-01',
               'batch_id': 1, 'examples': {}, 'last_reviewed': None, 'known': False}]
    data_manager.save_vocab(sample)
    assert data_manager.load_vocab() == sample
    minimal = [{'root': 'Baum', 'english': 'tree'}]
    vocab_file.write_text(json.dumps(minimal), encoding='utf-8')
    loaded = data_manager.load_vocab()
    assert len(loaded) == 1
    for field in data_manager.VOCAB_SCHEMA_FIELDS:
        assert field in loaded[0]


def test_load_save_memory(tmp_path, monkeypatch):
    mem_file = tmp_path / 'memory.json'
    monkeypatch.setattr(data_manager, 'MEMORY_FILE', mem_file)
    assert data_manager.load_memory() == {}
    mem = {'2023-01-01': {'notes': 'Test'}}
    data_manager.save_memory(mem)
    assert data_manager.load_memory() == mem


def test_is_new_word(monkeypatch):
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: [{'root': 'Haus'}, {'root': 'Baum'}])
    assert not data_manager.is_new_word('haus')
    assert not data_manager.is_new_word('BAUM')
    assert data_manager.is_new_word('Wasser')


def test_days_since_last_batch(monkeypatch):
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: [])
    assert data_manager.days_since_last_batch() == math.inf
    today = date.today()
    yesterday = today - timedelta(days=1)
    entries = [{'taught_on': today.isoformat()}, {'taught_on': yesterday.isoformat()}, {'taught_on': 'invalid'}]
    monkeypatch.setattr(data_manager, 'load_vocab', lambda: entries)
    assert data_manager.days_since_last_batch() == 0


def test_append_memory(tmp_path, monkeypatch):
    mem_file = tmp_path / 'memory.json'
    monkeypatch.setattr(data_manager, 'MEMORY_FILE', mem_file)
    data_manager.append_memory('2023-01-02', {'level': 'A1'})
    content = json.loads(mem_file.read_text(encoding='utf-8'))
    assert content.get('2023-01-02') == {'level': 'A1'}


def test_list_and_load_sessions(tmp_path, monkeypatch):
    chat_file = tmp_path / 'chat.json'
    monkeypatch.setattr(data_manager, 'CHAT_SESSIONS_FILE', chat_file)
    assert data_manager.list_sessions() == []
    assert data_manager.load_session('sess') == []
    sample = {'s1': [{'role': 'user', 'text': 'hi'}], 's2': []}
    chat_file.write_text(json.dumps(sample), encoding='utf-8')
    assert set(data_manager.list_sessions()) == set(sample.keys())
    assert data_manager.load_session('s1') == sample['s1']
    assert data_manager.load_session('nope') == []


def test_trim_messages(monkeypatch):
    class DummyEnc:
        def encode(self, text):
            return list(text)

    monkeypatch.setattr(data_manager.tiktoken, 'encoding_for_model', lambda model: DummyEnc())
    msgs = [{'text': 'aaa'}, {'text': 'bb'}, {'text': 'c'}]
    trimmed = data_manager.trim_messages(msgs, max_tokens=4)
    assert trimmed == msgs[1:]


def test_append_message(tmp_path, monkeypatch):
    chat_file = tmp_path / 'chat.json'
    monkeypatch.setattr(data_manager, 'CHAT_SESSIONS_FILE', chat_file)
    monkeypatch.setattr(data_manager, 'trim_messages', lambda msgs, max_tokens=600000: msgs)
    res1 = data_manager.append_message('s1', 'user', 'hello')
    assert res1 == [{'role': 'user', 'text': 'hello'}]
    saved = json.loads(chat_file.read_text(encoding='utf-8'))
    assert saved['s1'] == res1
    res2 = data_manager.append_message('s1', 'assistant', 'world')
    assert res2 == [{'role': 'user', 'text': 'hello'}, {'role': 'assistant', 'text': 'world'}]
    saved2 = json.loads(chat_file.read_text(encoding='utf-8'))
    assert saved2['s1'] == res2
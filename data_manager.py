"""Data I/O and scheduling utilities for German Tutor."""

import json
import math
from datetime import date
from pathlib import Path

import tiktoken

BASE_DIR = Path(__file__).resolve().parent
VOCAB_FILE = BASE_DIR / "vocab.json"
MEMORY_FILE = BASE_DIR / "memory.json"
CHAT_SESSIONS_FILE = BASE_DIR / "chat_sessions.json"

VOCAB_SCHEMA_FIELDS = [
    "root",
    "english",
    "taught_on",
    "batch_id",
    "examples",
    "last_reviewed",
    "known",
]

def load_vocab():
    """Load the vocabulary list from vocab.json."""
    try:
        data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    for entry in data:
        for field in VOCAB_SCHEMA_FIELDS:
            if field not in entry:
                if field == "examples":
                    entry[field] = {}
                elif field == "last_reviewed":
                    entry[field] = None
                elif field == "known":
                    entry[field] = False
                else:
                    entry[field] = None
    return data

def save_vocab(vocab_list):
    """Save the vocabulary list to vocab.json."""
    VOCAB_FILE.write_text(
        json.dumps(vocab_list, indent=2, ensure_ascii=False), encoding="utf-8"
    )

def load_memory():
    """Load memory checkpoints from memory.json."""
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}

def save_memory(memory_dict):
    """Save memory checkpoints to memory.json."""
    MEMORY_FILE.write_text(
        json.dumps(memory_dict, indent=2, ensure_ascii=False), encoding="utf-8"
    )

def is_new_word(root_word):
    """Return True if root_word not already present in vocab (case-insensitive)."""
    vocab = load_vocab()
    lower = root_word.lower()
    return not any(entry.get("root", "").lower() == lower for entry in vocab)

def days_since_last_batch():
    """Return number of days since the most recent 'taught_on' date in vocab.json."""
    vocab = load_vocab()
    dates = []
    for entry in vocab:
        taught = entry.get("taught_on")
        if taught:
            try:
                dates.append(date.fromisoformat(taught))
            except ValueError:
                continue
    if not dates:
        return math.inf
    last = max(dates)
    return (date.today() - last).days

def append_memory(date_str, entry_dict):
    """Add an entry to memory.json under the given date key."""
    memory = load_memory()
    memory[date_str] = entry_dict
    save_memory(memory)

def list_sessions():
    """List all chat session IDs in chat_sessions.json."""
    try:
        data = json.loads(CHAT_SESSIONS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    return list(data.keys())

def load_session(session_id):
    """Load the message list for a given session_id."""
    try:
        data = json.loads(CHAT_SESSIONS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    return data.get(session_id, [])

def trim_messages(messages, max_tokens=600000):
    """Trim oldest messages so total token count does not exceed max_tokens."""
    enc = tiktoken.encoding_for_model("gpt-4")
    counts = [len(enc.encode(m.get("text", ""))) for m in messages]
    total = sum(counts)
    trimmed = messages.copy()
    trimmed_counts = counts.copy()
    while trimmed and total > max_tokens:
        total -= trimmed_counts.pop(0)
        trimmed.pop(0)
    return trimmed

def append_message(session_id, role, text, max_tokens=600000):
    """Append a message to a chat session, trimming history by token count."""
    try:
        data = json.loads(CHAT_SESSIONS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        data = {}
    session = data.get(session_id, [])
    session.append({"role": role, "text": text})
    session = trim_messages(session, max_tokens=max_tokens)
    data[session_id] = session
    CHAT_SESSIONS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return session

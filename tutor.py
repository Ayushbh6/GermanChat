"""Core tutoring logic for German Tutor."""
import json
import random
from datetime import date

from openai import OpenAI

import data_manager

client = OpenAI()

def generate_new_batch(n_words):
    """Generate and append a new batch of words if the interval has elapsed."""
    if data_manager.days_since_last_batch() < 3:
        return []
    vocab = data_manager.load_vocab()
    next_id = 1 + max((e.get("batch_id") or 0) for e in vocab) if vocab else 1
    today = date.today().isoformat()
    prompt = (
        f"Generate {n_words} German vocabulary words with their English meanings "
        "and examples in present, past, and future tense. Respond in JSON format "
        "as a list of objects with keys: root, english, examples "
        "where examples is a dict with keys present, past, future and lists of sentences."
    )
    response = client.responses.create(
        model="o4-mini",
        input=[
            {
                "role": "system",
                "text": (
                    "You are a caring, patient, and professional German language tutor teaching an A2-level student. "
                    "Design your responses and examples to suit the A2 level."
                ),
            },
            {"role": "system", "text": prompt},
        ],
        text={"format": {"type": "text"}},
        reasoning={"effort": "medium"},
        tools=[],
        store=True,
    )
    try:
        candidates = json.loads(response.output_text)
    except Exception as e:
        raise RuntimeError("Failed to parse model output for new batch") from e

    new_entries = []
    for item in candidates:
        root = item.get("root")
        if not root or not data_manager.is_new_word(root):
            continue
        entry = {
            "root": root,
            "english": item.get("english"),
            "examples": item.get("examples", {}),
            "taught_on": today,
            "batch_id": next_id,
            "last_reviewed": None,
            "known": False,
        }
        vocab.append(entry)
        new_entries.append(entry)
    if new_entries:
        data_manager.save_vocab(vocab)
    return new_entries

def prepare_quiz(n_questions):
    """Select entries and format quiz questions with distractors."""
    vocab = data_manager.load_vocab()
    if not vocab or n_questions <= 0:
        return []
    selection = random.sample(vocab, min(n_questions, len(vocab)))
    quiz = []
    for item in selection:
        root = item.get("root")
        answer = item.get("english")
        others = [e.get("english") for e in vocab if e.get("root") != root]
        count = min(3, len(others))
        distractors = random.sample(others, count) if count > 0 else []
        quiz.append({
            "root": root,
            "expected_answer": answer,
            "distractors": distractors,
        })
    return quiz

def write_memory(entry_dict):
    """Delegate memory checkpoint entries to the data manager."""
    key = date.today().isoformat()
    data_manager.append_memory(key, entry_dict)

def chat_session_interact(session_id, user_message):
    """Manage a multi-turn chat session using GPT-4.1, persisting history."""
    history = data_manager.load_session(session_id)
    trimmed = data_manager.trim_messages(history)
    data_manager.append_message(session_id, "user", user_message)
    system_message = {
        "role": "system",
        "text": (
            "You are a caring, patient, and professional German language tutor teaching an A2-level student. "
            "Tailor your responses and examples to the A2 level. "
            "Always write the main sentences and vocabulary in German, but provide explanations of grammar, vocabulary, and concepts in English, "
            "unless the student explicitly requests explanations in German. "
            "Maintain a supportive and encouraging tone."
        ),
    }
    context = [system_message] + trimmed + [{"role": "user", "text": user_message}]
    response = client.responses.create(
        model="gpt-4.1",
        input=context,
    )
    reply = response.output_text
    data_manager.append_message(session_id, "assistant", reply)
    return reply
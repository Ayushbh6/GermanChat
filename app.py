"""
Streamlit app entrypoint for German Tutor.
Provides Chat Tutor and Flashcards modes.
"""

import random
from datetime import date, datetime

import streamlit as st

import data_manager
import tutor


def run_chat_tutor():
    """Render and manage the Chat Tutor mode."""
    st.title("Chat Tutor")
    # Session selection/creation
    sessions = data_manager.list_sessions()
    session_option = ["New Session"] + sessions
    session_key = st.sidebar.selectbox("Select session", session_option)
    if session_key == "New Session":
        session_id = datetime.now().isoformat()
    else:
        session_id = session_key
    # Load existing history
    history = data_manager.load_session(session_id)
    # Display chat history
    for msg in history:
        if msg.get("role") == "user":
            st.markdown(f"**You:** {msg.get('text')}")
        else:
            st.markdown(f"**Tutor:** {msg.get('text')}")

    # Action buttons
    if st.button("Teach me 20 new words", key="teach"):
        new_entries = tutor.generate_new_batch(20)
        st.write(f"Added {len(new_entries)} new words.")

    if st.button("Take Quiz", key="quiz"):
        quiz = tutor.prepare_quiz(5)
        for q in quiz:
            st.write(f"Translate: {q['root']}")
            choices = q.get("distractors", []) + [q.get("expected_answer")]
            random.shuffle(choices)
            st.radio("", choices, key=f"quiz_{q.get('root')}")

    if st.button("Write to memory", key="memory"):
        with st.form("memory_form"):
            level = st.text_input("Level")
            notes = st.text_area("Notes")
            if st.form_submit_button("Save Memory"):
                tutor.write_memory({"level": level, "notes": notes})
                st.success("Memory saved.")

    # Chat input
    user_input = st.text_input("You:", key="chat_input")
    if st.button("Send", key="send") and user_input:
        reply = tutor.chat_session_interact(session_id, user_input)
        st.markdown(f"**Tutor:** {reply}")


def run_flashcards():
    """Render and manage the Flashcards mode."""
    st.title("Flashcards")
    vocab = data_manager.load_vocab()
    if not vocab:
        st.write("No vocabulary available. Generate new words in Chat Tutor.")
        return

    cols = st.columns(3)
    for idx, entry in enumerate(vocab):
        col = cols[idx % 3]
        col.subheader(f"{entry.get('root')} - {entry.get('english')}")
        if col.button("Show Examples", key=f"show_{idx}"):
            col.write(entry.get("examples", {}))
        if col.button("Known", key=f"known_{idx}"):
            entry["known"] = True
            entry["last_reviewed"] = date.today().isoformat()
            data_manager.save_vocab(vocab)
        if col.button("Unknown", key=f"unknown_{idx}"):
            entry["known"] = False
            entry["last_reviewed"] = date.today().isoformat()
            data_manager.save_vocab(vocab)


def main():
    """Streamlit mode selector."""
    st.sidebar.title("Mode")
    mode = st.sidebar.radio("Go to:", ["Chat Tutor", "Flashcards"])
    if mode == "Chat Tutor":
        run_chat_tutor()
    else:
        run_flashcards()


if __name__ == "__main__":
    main()
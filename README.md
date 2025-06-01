# German Tutor Streamlit App

A lightweight Streamlit application that serves as your personal German tutor, helping you learn new vocabulary systematically and track your progress over time.

## 🎯 Features

### Core Learning Features
- **Structured Vocabulary Learning**: Learn 20 new German words every 3 days with examples in past, present, and future tenses
- **Smart Duplicate Prevention**: Automatically avoids teaching words you've already learned (case-insensitive)
- **Weekly Quizzes**: Generated from your accumulated vocabulary with multiple-choice and fill-in-the-blank questions
- **Progress Tracking**: On-demand memory checkpoints to track your learning journey

### Interactive Modes
- **Chat Tutor**: Conversational interface powered by GPT-4.1 for dynamic, multi-turn tutoring sessions
- **Flashcards**: Visual card-based review system with spaced repetition features
- **Session Management**: Persistent chat history across sessions with intelligent context management

### AI-Powered Learning
- **GPT-o4-mini**: Generates structured lessons with 20 new words and tense examples
- **GPT-4.1**: Powers conversational interactions with 1M token context window for rich tutoring sessions

## 🏗️ Architecture

```
┌───────────────────────────┐       ┌───────────────────┐
│       Streamlit UI        │◄──────│   Tutor Logic     │
│       (app.py)            │       │   (tutor.py)      │
└───────────────────────────┘       └───────────────────┘
             │                                  │
             ▼                                  ▼
       User Actions                   Data Management & Scheduling
             │                                  │
             ▼                                  ▼
       Quiz / Word                ┌────────────────────────┐
       Generation                 │ JSON Storage & I/O     │
       (Streamlit)                │ (data_manager.py)      │
                                   └────────────────────────┘
```

## 📁 Project Structure

```
./
├── app.py              # Streamlit UI and entrypoint
├── tutor.py            # Core tutoring logic (word selection, quiz prep)
├── data_manager.py     # JSON read/write utilities + scheduling helpers
├── vocab.json          # Persistent vocabulary store (auto-generated)
├── memory.json         # User progress checkpoints (auto-generated)
├── chat_sessions.json  # Persisted chat histories (auto-generated)
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ayushbh6/GermanChat.git
   cd GermanChat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**
   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501` to start learning!

## 🎮 How to Use

### Chat Tutor Mode
1. Select "Chat Tutor" from the sidebar
2. Click "Teach me 20 new words" to start a new lesson
3. Engage in conversation with the AI tutor
4. Use "Write to memory" to save progress checkpoints

### Flashcards Mode
1. Select "Flashcards" from the sidebar
2. Review cards showing German words and their English meanings
3. Flip cards to see usage examples in different tenses
4. Mark cards as Known/Unknown for spaced repetition

### Session Management
- Previous chat sessions are listed in the sidebar
- Click on any session to resume the conversation
- Context is automatically managed to stay within token limits

## 📊 Data Storage

The app uses three JSON files for data persistence:

### `vocab.json`
Stores all learned vocabulary with metadata:
```json
[
  {
    "root": "lernen",
    "english": "to learn",
    "taught_on": "2023-08-21",
    "batch_id": 5,
    "examples": {
      "present": ["Ich lerne Deutsch."],
      "past": ["Ich lernte Deutsch."],
      "future": ["Ich werde Deutsch lernen."]
    },
    "last_reviewed": "2023-08-28",
    "known": false
  }
]
```

### `memory.json`
User progress checkpoints:
```json
{
  "2023-01-03": {
    "level": "A1",
    "notes": "I struggle with adjective endings."
  }
}
```

### `chat_sessions.json`
Persistent chat histories:
```json
{
  "session_2023-09-01T10:00:00": [
    {"role": "user", "text": "Hello! Teach me..."},
    {"role": "assistant", "text": "Sure! Let's start with..."}
  ]
}
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Customization
- **Learning Schedule**: Modify the 3-day interval in `tutor.py`
- **Batch Size**: Change the default 20 words per batch
- **Quiz Settings**: Adjust quiz length and difficulty
- **Context Window**: Modify the ~600,000 token limit for chat sessions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues or have questions:
1. Check the existing [Issues](https://github.com/Ayushbh6/GermanChat/issues)
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🎯 Roadmap

- [ ] Add support for other languages
- [ ] Implement advanced spaced repetition algorithms
- [ ] Add pronunciation features
- [ ] Create mobile-responsive design
- [ ] Add grammar exercises
- [ ] Implement user authentication
- [ ] Add progress analytics and charts

---

**Happy Learning! 🇩🇪**

*Built with ❤️ using Streamlit and OpenAI* 
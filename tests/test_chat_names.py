import os

os.environ.setdefault("GROQ_API_KEY", "test-key")

from streamlit_frontend_database import build_chat_title


def test_build_chat_title_from_first_message():
    assert build_chat_title("What is machine learning and deep learning today?") == "What is machine learning and deep learning today?"


def test_build_chat_title_truncates_long_text():
    long_text = "This is a very long chat prompt about multiple topics and should be shortened for the sidebar label"
    assert build_chat_title(long_text) == "This is a very long chat prompt about multiple topics and should be shortened..."

# LangGraph Chatbot

This project is a tool-enabled chatbot built with Python, LangGraph, and Streamlit. It uses a LangGraph state graph with a SQLite checkpointer so conversations can be stored and resumed across threads.

## Features

- Chat interface built with Streamlit
- LangGraph workflow with conditional tool execution
- DuckDuckGo web search
- Stock price lookup through Alpha Vantage
- Calculator tool for addition, subtraction, multiplication, and division
- Streaming assistant responses with visible tool-use status
- SQLite-backed conversation checkpointing
- Multiple conversations with names based on the first user message
- Optional LangSmith tracing for debugging and observability
- New chat creation and conversation switching in the sidebar

## Project Structure

- `langgraph_database_tools_backend.py` - backend LangGraph graph, tools, and database setup
- `streamlit_frontend_database.py` - Streamlit frontend UI
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.10+
- A Groq API key
- Virtual environment recommended

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv myenv
myenv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Groq key:

```env
GROQ_API_KEY=your_api_key_here
```

## LangSmith Tracing

The app supports optional LangSmith tracing for inspecting LangGraph runs, model calls, tool calls, and errors. Add these settings to `.env` to enable it:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=langgraph-chatbot
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

Restart Streamlit after changing `.env`. When tracing is disabled or the LangSmith variables are not configured, the chatbot continues to run without sending traces.

## Run the app

```bash
streamlit run streamlit_frontend_database.py
```

## Tools

The model can select tools when a request needs them:

- **Web search** - searches the web using DuckDuckGo.
- **Stock prices** - retrieves the latest quote for a symbol using Alpha Vantage.
- **Calculator** - performs `add`, `sub`, `mul`, and `div` operations and reports invalid operations or division by zero.

Tool calls run through LangGraph's `ToolNode` and conditional routing. The Streamlit interface displays the active tool while the assistant response is being generated.

## Notes

- The app stores chat checkpoints locally in the SQLite database file `chatbot.db`.
- Keep `.env`, `chatbot.db`, and the `myenv/` virtual environment local; they should not be committed to Git.
- If you want to stop using a conversation thread, you can create a new one from the sidebar.

## Future Improvements

- Conversation delete/edit actions
- More polished Streamlit UI
- Persistent user authentication or session management

# LangGraph Chatbot with RAG

This project is a LangGraph-powered chatbot built with Python, Streamlit, and RAG (Retrieval-Augmented Generation). It supports multi-turn chat, document-based Q&A, and tool calling, while keeping each conversation in a separate thread with SQLite checkpointing.

## Features

- Streamlit chat interface
- LangGraph workflow with tool routing
- PDF upload and indexing per chat/thread
- RAG search over uploaded PDF content
- Web search using DuckDuckGo
- Stock price lookup using Alpha Vantage
- Simulated stock purchases with human approval
- Calculator tool for arithmetic operations
- SQLite-backed conversation memory across threads
- Sidebar chat list with names generated from the first user message
- Optional LangSmith tracing for debugging and observability
- New chat creation and switching between conversation threads

## Project Structure

- `langgraph_database_tools_backend.py` - LangGraph graph, tools, PDF indexing, and retriever logic
- `streamlit_frontend_database.py` - Streamlit UI and chat/thread management
- `requirements.txt` - Python package dependencies
- `tests/test_chat_names.py` - simple validation for chat title generation

## Requirements

- Python 3.10+
- Groq API key
- Virtual environment recommended
- PDF support through FAISS and sentence-transformers

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

3. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
```

Optional LangSmith configuration:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=langgraph-chatbot
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

## Run the app

```bash
streamlit run streamlit_frontend_database.py
```

## How RAG works

1. Upload a PDF from the sidebar.
2. The document is split into chunks.
3. Each chunk is embedded using Hugging Face embeddings.
4. A FAISS vector store is created for that specific thread.
5. When the user asks a question about the document, the agent calls the `rag_tool` and retrieves relevant document context.
6. The answer is generated using the retrieved context + the LLM.

This makes the chatbot capable of answering questions from uploaded PDFs while still using other tools like search, calculator, stock lookup, and stock purchase simulation when needed.

## Tools

The model can call tools during a chat:

- **PDF RAG** - answers questions using the uploaded PDF content for the current thread
- **Web search** - searches the web using DuckDuckGo
- **Stock prices** - fetches the latest quote for a symbol using Alpha Vantage
- **Purchase stock** - simulates purchasing a selected quantity of shares and asks for human approval before confirming
- **Calculator** - performs `add`, `sub`, `mul`, and `div` operations

### Stock purchase approval

When the model calls `purchase_stock`, LangGraph pauses the workflow with an interrupt. The Streamlit interface displays the approval request and provides **Approve** and **Decline** buttons. The selected decision resumes the same conversation thread:

- Approving places a simulated order and returns a success message.
- Declining cancels the simulated order and returns a cancellation message.

The purchase tool does not execute a real trade.

## Conversation Memory

- Each chat is stored in a separate thread ID.
- The internal thread ID is still used for memory and retrieval.
- The sidebar shows a readable chat name based on the first user message, so it is easier to switch between conversations.
- Chat state is stored locally using SQLite in `chatbot.db`.

## Notes

- Keep `.env`, `chatbot.db`, and the `myenv/` folder local and do not commit them to Git.
- The app allows you to create a new chat from the sidebar at any time.
- If a PDF is uploaded for a thread, the retriever is stored only for that thread and not shared globally.

## Future Improvements

- Delete or rename chat sessions
- Better file and document management
- More polished Streamlit UI
- User authentication and session persistence

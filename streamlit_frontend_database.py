import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command

from langgraph_database_tools_backend import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)

st.title('AI CHATBOT ', icon=":material/chat:")
st.subheader(" :orange[This is an AI CHATBOT build using LANGGRAPH]", divider="gray")
st.badge("Active", icon=":material/check:", color="green")

# =========================== Utilities ===========================
def generate_thread_id():
    return uuid.uuid4()


def build_chat_title(text):
    cleaned = " ".join(str(text).strip().split())
    if not cleaned:
        return "New Chat"

    if len(cleaned) <= 40:
        return cleaned

    return cleaned[:37].rstrip() + "..."


def get_thread_title(thread_id):
    thread_id_key = str(thread_id)
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id_key}})

    if not state or not getattr(state, "values", None):
        return "New Chat"

    messages = state.values.get("messages", [])
    for message in messages:
        if isinstance(message, HumanMessage):
            return build_chat_title(message.content)

    for message in messages:
        if hasattr(message, "content"):
            return build_chat_title(message.content)

    return "New Chat"


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []
    st.session_state["pending_approval"] = None


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

if "pending_approval" not in st.session_state:
    st.session_state["pending_approval"] = None

add_thread(st.session_state["thread_id"])

thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})
threads = st.session_state["chat_threads"][::-1]
selected_thread = None

# ============================ Sidebar ============================
st.sidebar.title("LangGraph PDF Chatbot")
st.sidebar.markdown(f"**Chat:** {get_thread_title(thread_key)}")

if st.sidebar.button("New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

if thread_docs:
    latest_doc = list(thread_docs.values())[-1]
    st.sidebar.success(
        f"Using `{latest_doc.get('filename')}` "
        f"({latest_doc.get('chunks')} chunks from {latest_doc.get('documents')} pages)"
    )
else:
    st.sidebar.info("No PDF indexed yet.")

uploaded_pdf = st.sidebar.file_uploader("Upload a PDF for this chat", type=["pdf"])
if uploaded_pdf:
    if uploaded_pdf.name in thread_docs:
        st.sidebar.info(f"`{uploaded_pdf.name}` already processed for this chat.")
    else:
        with st.sidebar.status("Indexing PDF…", expanded=True) as status_box:
            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name,
            )
            thread_docs[uploaded_pdf.name] = summary
            status_box.update(label="✅ PDF indexed", state="complete", expanded=False)

st.sidebar.subheader("Past conversations")
if not threads:
    st.sidebar.write("No past conversations yet.")
else:
    for thread_id in threads:
        chat_name = get_thread_title(thread_id)
        if st.sidebar.button(chat_name, key=f"side-thread-{thread_id}"):
            selected_thread = thread_id

# ============================ Main Layout ========================
st.title("Multi Utility Chatbot")

# Chat area
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

pending_approval = st.session_state["pending_approval"]
if pending_approval:
    st.warning(pending_approval["prompt"])
    approval_col, decline_col = st.columns(2)
    with approval_col:
        approve = st.button("Approve", type="primary", use_container_width=True)
    with decline_col:
        decline = st.button("Decline", use_container_width=True)

    if approve or decline:
        decision = "yes" if approve else "no"
        result = chatbot.invoke(
            Command(resume=decision),
            config=pending_approval["config"],
        )
        st.session_state["pending_approval"] = None
        last_message = result["messages"][-1]
        st.session_state["message_history"].append(
            {"role": "assistant", "content": last_message.content}
        )
        st.rerun()

user_input = None if st.session_state["pending_approval"] else st.chat_input(
    "Ask about your document or use tools"
)

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": thread_key},
        "metadata": {"thread_id": thread_key},
        "run_name": "chat_turn",
    }

    result = chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=CONFIG,
    )
    interrupts = result.get("__interrupt__", [])
    if interrupts:
        st.session_state["pending_approval"] = {
            "prompt": interrupts[0].value,
            "config": CONFIG,
        }
        st.rerun()

    last_message = result["messages"][-1]
    with st.chat_message("assistant"):
        st.text(last_message.content)
    st.session_state["message_history"].append(
        {"role": "assistant", "content": last_message.content}
    )

    doc_meta = thread_document_metadata(thread_key)
    if doc_meta:
        st.caption(
            f"Document indexed: {doc_meta.get('filename')} "
            f"(chunks: {doc_meta.get('chunks')}, pages: {doc_meta.get('documents')})"
        )

st.divider()

if selected_thread:
    st.session_state["thread_id"] = selected_thread
    messages = load_conversation(selected_thread)

    temp_messages = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        temp_messages.append({"role": role, "content": msg.content})
    st.session_state["message_history"] = temp_messages
    st.session_state["ingested_docs"].setdefault(str(selected_thread), {})
    st.rerun()
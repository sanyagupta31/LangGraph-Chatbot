import streamlit as st
from langgraph_database_backend import chatbot,retreive_all_threads
from langchain_core.messages import HumanMessage
import uuid


st.title('AI CHATBOT ', icon=":material/chat:")
st.subheader(" :orange[This is an AI CHATBOT build using LANGGRAPH]", divider="gray")
st.badge("Active", icon=":material/check:", color="green")


def generate_thread_id():
    return str(uuid.uuid4())


def generate_thread_name():
    return "New Chat"


def get_first_user_message_name(messages):
    for message in messages:
        if isinstance(message, HumanMessage):
            text = str(message.content).strip()
            if text:
                return text[:30] + ('...' if len(text) > 30 else '')
    return "New Chat"


def reset_chat():
    thread_id = generate_thread_id()
    thread_name = generate_thread_name()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id, thread_name)
    st.session_state['message_history'] = []


def normalize_chat_threads(threads):
    normalized = []
    for item in threads:
        if isinstance(item, dict):
            normalized.append({
                'id': item.get('id') or item.get('thread_id'),
                'name': item.get('name') or str(item.get('id') or item.get('thread_id'))
            })
        else:
            normalized.append({
                'id': str(item),
                'name': str(item)
            })
    return normalized


def add_thread(thread_id, thread_name=None):
    st.session_state['chat_threads'] = normalize_chat_threads(st.session_state.get('chat_threads', []))

    if thread_name is None:
        try:
            messages = load_conversation(thread_id)
            thread_name = get_first_user_message_name(messages)
        except Exception:
            thread_name = "New Chat"

    existing = next((t for t in st.session_state.get('chat_threads', []) if t.get('id') == thread_id), None)
    if existing is None:
        st.session_state['chat_threads'].append({
            'id': thread_id,
            'name': thread_name
        })
    elif existing.get('name') == 'New Chat':
        existing['name'] = thread_name


def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    if state is None or state.values is None:
        return []
    return state.values.get('messages', [])


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retreive_all_threads()

st.session_state['chat_threads'] = normalize_chat_threads(st.session_state.get('chat_threads', []))
add_thread(st.session_state['thread_id'], generate_thread_name())


### sidebar
st.sidebar.title('Langgraph Chatbot')
if st.sidebar.button(':red[New Chat]'):
    reset_chat()
st.sidebar.header('My Conversations')
for thread in st.session_state['chat_threads'][::-1]:
    thread_name = thread.get('name', str(thread.get('id', 'Chat')))
    if st.sidebar.button(thread_name):
        st.session_state['thread_id'] = thread['id']
        messages = load_conversation(thread['id'])
        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': message.content})
        st.session_state['message_history'] = temp_messages


for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

user_input=st.chat_input('Type here')
if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})
    current_thread = next((t for t in st.session_state['chat_threads'] if t['id'] == st.session_state['thread_id']), None)
    if current_thread and current_thread['name'] == 'New Chat':
        current_thread['name'] = user_input[:30] + ('...' if len(user_input) > 30 else '')

    with st.chat_message('user'):
        st.text(user_input)

    with st.spinner("AI is typing..."):
        with st.chat_message('assistant'):
            ai_message=st.write_stream(
                        message_chunk for message_chunk , metadata in chatbot.stream(
                    {'messages': [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode='messages'
                )
            )
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})   

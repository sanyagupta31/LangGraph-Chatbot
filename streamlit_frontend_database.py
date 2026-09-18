import streamlit as st
from langgraph_database_tools_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import uuid


st.title('AI CHATBOT ', icon=":material/chat:")
st.subheader(" :orange[This is an AI CHATBOT build using LANGGRAPH]", divider="gray")
st.badge("Active", icon=":material/check:", color="green")


def generate_thread_id():
    return str(uuid.uuid4())



def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []



def add_thread(thread_id, thread_name=None):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    if state is None or state.values is None:
        return []
    return state.values.get('messages', [])


def get_thread_name(thread_id):
    for message in load_conversation(thread_id):
        if isinstance(message, HumanMessage) and message.content.strip():
            thread_name = ' '.join(message.content.split())
            return thread_name[:40] + ('...' if len(thread_name) > 40 else '')
    return 'New conversation'


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()


add_thread(st.session_state['thread_id'])


### sidebar
st.sidebar.title('Langgraph Chatbot')
if st.sidebar.button(':red[New Chat]'):
    reset_chat()
st.sidebar.header('My Conversations')
for thread_id in st.session_state['chat_threads'][::-1]:
    thread_name = get_thread_name(thread_id)
    if st.sidebar.button(thread_name, key=f'thread_{thread_id}'):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)
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


        

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']},"metadata":{"thread_id":st.session_state["thread_id"]},"run_name":"chat_turn",}

user_input=st.chat_input('Type here')
if user_input:

    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
         st.text(user_input)

   

    with st.spinner("AI is typing..."):
        with st.chat_message("assistant"):
                # Use a mutable holder so the generator can set/modify it
                status_holder = {"box": None}
        
                def ai_only_stream():
                    for message_chunk, metadata in chatbot.stream(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages",
                    ):
                        # Lazily create & update the SAME status container when any tool runs
                        if isinstance(message_chunk, ToolMessage):
                            tool_name = getattr(message_chunk, "name", "tool")
                            if status_holder["box"] is None:
                                status_holder["box"] = st.status(
                                    f"🔧 Using `{tool_name}` …", expanded=True
                                )
                            else:
                                status_holder["box"].update(
                                    label=f"🔧 Using `{tool_name}` …",
                                    state="running",
                                    expanded=True,
                                )
        
                        # Stream ONLY assistant tokens
                        if isinstance(message_chunk, AIMessage):
                            yield message_chunk.content
        
                ai_message = st.write_stream(ai_only_stream())
        
                # Finalize only if a tool was actually used
                if status_holder["box"] is not None:
                    status_holder["box"].update(
                        label="✅ Tool finished", state="complete", expanded=False
                    )
        
            # Save assistant message
    st.session_state["message_history"].append(
                {"role": "assistant", "content": ai_message}
            )
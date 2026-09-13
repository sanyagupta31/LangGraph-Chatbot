from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict,Annotated
from dotenv import load_dotenv
import os
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3

load_dotenv()
model=ChatGroq(model="openai/gpt-oss-120b", groq_api_key=os.environ["GROQ_API_KEY"])
class chatstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
def chat_node(state:chatstate):
    messages=state['messages']
    response=model.invoke(messages)
    return {'messages':[response]}

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)
graph=StateGraph(chatstate)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)
chatbot=graph.compile(checkpointer=checkpointer)

def retreive_all_threads():
    all_threads = []
    seen = set()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        if thread_id not in seen:
            seen.add(thread_id)
            all_threads.append({
                'id': thread_id,
                'name': f'Chat {len(all_threads) + 1}'
            })
    return all_threads

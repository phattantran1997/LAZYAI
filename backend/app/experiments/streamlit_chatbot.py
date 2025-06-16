import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
st.title("Chatbot")
# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(SystemMessage("You are a learning assistant. Do not give direct answers—only offer hints, guiding questions, or recommendations to help the student think through the problem. Focus on promoting understanding and critical thinking, not efficiency. Encourage exploration, point out useful strategies, and highlight common pitfalls, but let the student do the reasoning themselves."))
# display chat messages from history on app rerun
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)
prompt = st.chat_input("How are you?")
if prompt:
    # add the message from the user (prompt) to the screen with streamlit
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))
    # initialize model 
    llm = ChatOllama(
        model="llama3.2",
        temperature=2
    )
    result = llm.invoke(st.session_state.messages).content
    with st.chat_message("assistant"):
        st.markdown(result)
        st.session_state.messages.append(AIMessage(result))
"""
Fine tuning Llama 3.2 model at Notebook:
Huggingface: https://huggingface.co/volam1311/outputs
"""
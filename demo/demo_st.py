import streamlit as st
from models.chatbot_model import ChatbotModel
from utils.helpers import load_all_scene_configs

st.set_page_config(
    page_title="ChatGLM2-6b 演示",
    page_icon=":robot:",
    layout='wide'
)

chatbot_model = ChatbotModel(load_all_scene_configs())

st.title("ChatGLM2-6B")

max_length = st.sidebar.slider('max_length', 0, 32768, 8192, step=1)
top_p = st.sidebar.slider( 'top_p', 0.0, 1.0, 0.8, step=0.01)
temperature = st.sidebar.slider( 'temperature', 0.0, 1.0, 0.8, step=0.01)

if 'history' not in st.session_state:
    st.session_state.history = []

for i, message in enumerate(st.session_state.history):
    if message["role"] == "user":
        with st.chat_message(name="user", avatar="user"):
            st.markdown(message["content"])
    else:
        with st.chat_message(name="assistant", avatar="assistant"):
            st.markdown(message["content"])

with st.chat_message(name="user", avatar="user"):
    input_placeholder = st.empty()

with st.chat_message(name="assistant", avatar="assistant"):
    message_placeholder = st.empty()

prompt_text = st.text_area(label="用户命令输入",
                           height=100,
                           placeholder="请在这儿输入您的命令",
                           key="text_area_key")

button = st.button("发送", key="predict")

if button:
    input_placeholder.markdown(prompt_text)
    history = st.session_state.history
    response = chatbot_model.process_multi_question(prompt_text)
    message_placeholder.markdown(response)
    # history.append({"role":"user", "content": prompt_text})
    # history.append({"role":"assistant", "content": response})
    st.session_state.history = history


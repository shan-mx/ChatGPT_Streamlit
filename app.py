import time
from helper import *
import streamlit as st
import openai

st.set_page_config(page_title='GPT Assistant')
st.title('GPT Assistant')
user = "User" if "user" not in st.experimental_get_query_params() else st.experimental_get_query_params()["user"][0]
initial_content = "" if "initial_content" not in st.session_state else st.session_state["initial_content"]
api_key = "" if "api_key" not in st.session_state else st.session_state["api_key"]
if user or 'data' not in st.session_state:
    st.session_state['data'] = load_data(user, initial_content)
if "rerun" not in st.session_state:
    st.session_state["rerun"] = True
else:
    st.session_state.pop("rerun")
chat_stats = st.session_state['data']["chat_stats"]
chat_history = st.session_state['data']["chat_history"]
if st.session_state["data"]:
    show_messages(user, st.session_state['data']["chat_history"], st)
with st.form("form", clear_on_submit=True):
    user_input = st.text_area(f"**{user}:**", key="input")
    if st.form_submit_button("Submit", use_container_width=True):
        openai.api_key = api_key if api_key != "" else st.secrets["apikey"]
        chat_stats["Total Rounds"] += 1
        t1 = time.time()
        chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Processing..."):
            try:
                r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=chat_history)
            except openai.error.APIConnectionError:
                return_text = "[Warning] API Connection Error, try again."
            except openai.error.InvalidRequestError:
                return_text = "[Warning] Reached chat content limit, go Settings -> 'Clear Chat History'."
            except openai.error.RateLimitError:
                return_text = "[Warning] Reached chat rate limit, do not send request too frequently."
            else:
                return_text = r["choices"][0]["message"]["content"]
                chat_stats["Total Tokens"] += r["usage"]["total_tokens"]
                chat_stats["Tokens Used"] = r["usage"]["total_tokens"]
            chat_history.append({"role": "assistant", "content": return_text})
            chat_stats["Time Used"] = round(time.time() - t1, 3)
            chat_stats["Total Time"] += chat_stats["Time Used"]
            chat_stats["Averaged Time"] = round(chat_stats["Total Time"] / chat_stats["Total Rounds"], 3)
            save_data(chat_history, chat_stats, user)
            if "rerun" in st.session_state:
                st.experimental_rerun()
with st.expander("Settings"):
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state['data']["chat_history"] = [{"role": "system", "content": initial_content}]
        st.session_state['data']["chat_stats"] = initial_stats
        save_data(st.session_state['data']["chat_history"], st.session_state['data']["chat_stats"], user)
        st.experimental_rerun()
    user_box = st.text_input("Username (each user have their own chat data)", value=user)
    initial_content_box = st.text_input("Initial Instruction (applies when the chat history is cleared)", value=initial_content)
    api_key_box = st.text_input("OpenAI API Key (optional)", value=api_key)
    if user_box:
        st.experimental_set_query_params(user=user_box)
        if "rerun" in st.session_state:
            st.experimental_rerun()
    if initial_content_box:
        st.session_state["initial_content"] = initial_content_box
    if api_key_box:
        st.session_state["api_key"] = api_key_box
    st.write("GUI bulit by shan-mx")
with st.expander("Statistics"):
    col1, col2, col3 = st.columns(3)
    col1.metric("Time Used:", chat_stats["Time Used"])
    col1.metric("Averaged Time:", chat_stats["Averaged Time"])
    col2.metric("Tokens Used:", chat_stats["Tokens Used"])
    col2.metric("Total Tokens:", chat_stats["Total Tokens"])
    col3.metric("Total Rounds:", chat_stats["Total Rounds"])
